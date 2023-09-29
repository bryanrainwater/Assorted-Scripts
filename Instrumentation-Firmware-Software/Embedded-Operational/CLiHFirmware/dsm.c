//=============================================================================
// (c) Copyright 2014 Diamond Systems Corporation. Use of this source code
// is subject to the terms of Diamond Systems' Software License Agreement.
// Diamond Systems provides no warranty of proper performance if this
// source code is modified.
//
// File: ARIESDAConvert.c  v1.0
//  Depedency :	Universal Driver version 7.00
//				DSCUD.H - Include file.
//				
//				LIBDSCUD-7.00.a	- Library file for Linux 2.6.29-3.x
//						
//				DSCUD.LIB	- Static library file for Windows 
//						( USE VC++ 6.0 or Visual Studio 2005 )
// Description: This sample code demonstrates the usage of UD function
//				ARIESDAConvert(). This sample code describes the usage
//				for Aries board. Channel and 16-bit output code are prompted
//              from the user, then output to the board. Other settings are
//              controlled via the jumpers for this board.
//============================================================================

// #include "DSCUD_demo_def.h"

#include <stdio.h>
#include <stdarg.h>
#include <string.h>

// Linux and QNX
#include <stdlib.h>
#include <math.h>
//#include <time.h>
#include <termios.h>
#include <fcntl.h>
#include <unistd.h>

// diamond driver includes
#include "dscud.h"
#include "dscud_os.h"

#include "mpedaq0804.h"

#include "Aries.h"
//#define ARIES_DEFAULT_BASE_ADDRESS 0x280
//#define ARIES_DEFAULT_IRQ 5

#define CLK_SRC 1 //Use either 1 = cntr0 or 2 = cntr1


#include "dsm.h"


// globals
ERRPARAMS errorParams;          // structure for returning error code and error string

DSCB dscb = 0;                  // handle used to refer to the board
DSCCB dsccb;                    // structure containing ISA board settings
DSCCBP dsccbp;                   // structure containing board settings for PCI express and FeaturePak boards

DSCB DMMdscb = 0;
DSCCB DMMdsccb;
DSCCBP DMMdsccbp;
DSCADSETTINGS DMMdscadsettings;
DSCDASETTINGS DMMdscdasettings;
DSCS DMMdscs;
DSCAIOINT dscaioint;
DSCWGCONFIG dscWGconfig;


BoardInfo *bi=NULL;

ARIESINIT init;
ARIESADSETTINGS ARIESADSettings;  // structure containing A/D conversion settings
ARIESWAVEFORM waveform;
ARIESADINT dscIntSettings;      // structure containing A/D conversion interrupt settings
ARIESADINTSTATUS intstatus;     // structure containing A/D conversion interrupt status
ARIESUSERINT inter;
ARIESCOUNTER counter;
ARIESFIFO Ariesfifo;

//DAQ0804 specific settings
DAQ0804ADSETTINGS MPEadsettings;
DAQ0804ADINT	 MPEdscIntSettings;//  structure containing A/D conversion interrupt settings
DAQ0804ADINTSTATUS MPEintstatus;// structure containing A/D conversion interrupt status
DAQ0804COUNTER MPECtr;

DAQ0804USERINT MPEinter;//MPEcounter;

DSCB MPEdscb;
DSCCB MPEdsccb;
DSCCBP MPEdsccbp;

BoardInfo *MPEbi;
unsigned int MPESample[8];
int MPEDARange;
int MPEdasim;
unsigned long int DACode;


int portConfig[4];              //used to store the port directions
int portConfiguration[6];


char input_buffer[256];
char output_buffer[256];

int Each_Channel_Buffer_Size;
int No_OF_DA_Channel;

//int channel = 0;
int intBuff = 0, intBuff1 = 0; // tmp vars
//int temp = 0; //temp storage

BYTE return_value = 0;
float frequency;
int no_channel;

//int sample[8]; // sample reading
DFLOAT voltage;
//int scansize;
float rate = 0.0;

//Defined for user function for counting interrupt operations
int count = 0;
int MPEcounter = 0;
int DMMcount = 0;

//////////VERY IMPORTANT NOTE//////////////////////////////
//////////SETTING MPE CLOCK to 3 breaks EVERYTHING////////
/////////////////////////////////////////////////////////

#define ARIES_DEFAULT_BASE_ADDRESS 0x280
//Setting the IRQ to 7 seems to resolve spectral shift (non-walking)
//Also seems to resolve issues with fails every other restart
//Disables interrupts
#define ARIES_DEFAULT_IRQ 0x5

#define MAX_AD_CHANNEL_NUMBER 16
#define MAX_DA_CHANNEL_NUMBER 4


#define DACODE_MID 32768
#define DACODE_MAX 65535

#define MFCSCALE        0.5f // (MFC setpoint volts / MFC SLM)
#define PI              3.14159265f // Everybody loves pi!

#define SCANPTS         2048
//#define DA_OUTRATE      250000
#define DARANGE         65536
#define DAVOLTS         5.0f
//#define DARKINTERVAL    0
#define DARKINTERVAL    40


//#define NUM_WAVE_CHAN   2

//=============================================================================
int range;
int result;

SWORD *sample=NULL;

double VrefsAD[4] ={10.0,5.0,2.5,1.25};         // Voltage scale
double VrefsBip[4]={20.0,10.0,5.0,2.5};         // Gain

double MPEVrefs[2] = {5,10};
double MPEVrefsBip[2] = {10,20};


int VrefsDA[4]={5,10,5,10};
int LoadCal = 1;

int iindex,scansize,jIndex=0;   // miscellaneous

int DCscanRamp[SCANPTS];

//struct CONFIG config; //Parameters from config text file

void userfun()//void*)// param)// void *param )
  {
   //printf("This is the counter: %u\n", count);
   count ++;
  }

void MPEuserfun()//void*)
  {
   //printf("This is the MPE Counter: %u\n", MPEcounter++);
   MPEcounter ++;
  }

int DMMuserfun()
  {
   dscGetStatus(DMMdscb, &DMMdscs);
   return (int)(DMMdscs.total_transfers);
  }

//=========================================================================
// Initialize the interface board
//    I. DRIVER INITIALIZATION (U
//  II. BOARD INITIALIZATION
//
int initialize(int bufferSize, float waveFrequency, int laserNum, int numDAWaveChannels, int numADWaveChannels, int* scanBuffer)
  {
   //if ( (dscInit ( DSC_VERSION ) != DE_NONE) )
   //printf("DSC Version: %d\n", DSC_VERSION);
   if ( (dscInit ( DSC_VERSION ) != DE_NONE) )
     {
      dscGetLastError ( &errorParams );
      printf ( "dscInit error: %s %s\n", dscGetErrorString ( errorParams.ErrCode ), errorParams.errstring );
      return -1;
     }


   int laserTuning = 0;//FALSE;

   /*
   memset(&DMMdsccb, 0, sizeof(DSCCB));
   memset(&DMMdscb, 0, sizeof(DSCB));
   memset(&DMMdscs, 0, sizeof(DSCS));
   memset(&DMMdscadsettings, 0, sizeof(DSCADSETTINGS));
   memset(&DMMdscdasettings, 0, sizeof(DSCDASETTINGS));
   memset(&dscaioint, 0, sizeof(DSCAIOINT));


   DMMdsccb.boardtype = DSC_DMM32DX;
   DMMdsccb.base_address = 0x300;
   DMMdsccb.int_level = 7;//5;
   DMMdsccb.DAC_Config = 1;

   if (( dscInitBoard(DSC_DMM32DX, &DMMdsccb, &DMMdscb)) != DE_NONE )
     {
      dscGetLastError ( &errorParams );
      printf ( "dscInitBoard failed: %s %s\n", dscGetErrorString ( errorParams.ErrCode ), errorParams.errstring );
      return -1;
     }

   if(( dscEnhancedFeaturesEnable( DMMdscb, (BOOL)TRUE ))!= DE_NONE)
     {
      dscGetLastError ( &errorParams );
      printf ( "dscEnhancedFeaturesEnable failed: %s %s\n", dscGetErrorString ( errorParams.ErrCode ), errorParams.errstring );
      return -1;
     }


   //if (( autoCal())
   
   if (( dscADSetSettings(DMMdscb, &DMMdscadsettings)) != DE_NONE )
     {
      dscGetLastError ( &errorParams );
      printf ( "dscADSetSettings failed: %s %s\n", dscGetErrorString ( errorParams.ErrCode ), errorParams.errstring );
      return -1;
     }
   
   if (( dscDASetSettings(DMMdscb, &DMMdscdasettings)) != DE_NONE )
     {
      dscGetLastError ( &errorParams );
      printf ( "dscDASetSettings failed: %s %s\n", dscGetErrorString ( errorParams.ErrCode ), errorParams.errstring );
      return -1;
     }

   dscWGconfig.depth = (DWORD)1024;
   dscWGconfig.ch_per_frame = (DWORD)(0);
   dscWGconfig.source = (DWORD)1;//2;
   
   dscCounterSetRateSingle(DMMdscb, (float)200000, COUNTER_1_2);
   dscCounterSetRateSingle(DMMdscb, (float)200000, COUNTER_0);

   if (( dscWGCommand(DMMdscb, WG_CMD_RESET)) != DE_NONE )
     {
      dscGetLastError ( &errorParams );
      printf ( "dscWGCommand failed: %s %s\n", dscGetErrorString ( errorParams.ErrCode ), errorParams.errstring );
      return -1;
     }

   if (( dscWGConfigSet(DMMdscb, &dscWGconfig)) != DE_NONE )
     {
      dscGetLastError ( &errorParams );
      printf ( "dscWGConfigSet failed: %s %s\n", dscGetErrorString ( errorParams.ErrCode ), errorParams.errstring );
      return -1;
     }

   if (( dscWGCommand(DMMdscb, WG_CMD_RESET)) != DE_NONE )
     {
      dscGetLastError ( &errorParams );
      printf ( "dscWGCommand failed: %s %s\n", dscGetErrorString ( errorParams.ErrCode ), errorParams.errstring );
      return -1;
     }

   for( int i = 0; i < 1024; i++ )
     {
      //board, index, value, outchannel, unknown
      if( dscWGBufferSet(DMMdscb, i, 0, 1, 1) != DE_NONE )
        {
         dscGetLastError ( &errorParams );
         printf ( "dscWGBufferSet failed: %s %s\n", dscGetErrorString ( errorParams.ErrCode ), errorParams.errstring );
         return -1;
        }
     }

   dscGetStatus(DMMdscb, &DMMdscs);
  
   //SC_NSAMPLES*SC_PER_HK
   dscaioint.num_conversions = (int)(1024);//*(50*5 + 1);
   dscaioint.conversion_rate = 200000;
   dscaioint.cycle = (BYTE)TRUE;
   dscaioint.internal_clock = (BYTE)TRUE;
   dscaioint.low_channel = 0;
   dscaioint.high_channel = 0;
   dscaioint.external_gate_enable = (BYTE)FALSE;
   dscaioint.internal_clock_gate = (BYTE)TRUE;
   dscaioint.fifo_enab = (BYTE)TRUE;
   dscaioint.fifo_depth = (int)(1024/4);
   dscaioint.dump_threshold = (int)(1024/4);
   dscaioint.sample_values = (DSCSAMPLE*)malloc(sizeof(DSCSAMPLE) *
      dscaioint.num_conversions );

   //clock_gettime(CLOCK_MONOTONIC, &WGStartTime);

   
   if (( dscADScanInt(DMMdscb, &dscaioint)) != DE_NONE )
     {
      dscGetLastError ( &errorParams );
      printf ( "dscADScanInt failed: %s %s\n", dscGetErrorString ( errorParams.ErrCode ), errorParams.errstring );
      return -1;
     }

   if (( dscWGCommand(DMMdscb, WG_CMD_START)) != DE_NONE )
     {
      dscGetLastError ( &errorParams );
      printf ( "dscWGCommand failed: %s %s\n", dscGetErrorString ( errorParams.ErrCode ), errorParams.errstring );
      return -1;
     }

   */


   memset(&dsccb,0,sizeof(DSCCB));
   memset(&ARIESADSettings, 0, sizeof(ARIESADSETTINGS));
   memset(&dscIntSettings, 0, sizeof(ARIESADINT));
   memset(&intstatus, 0, sizeof(ARIESADINTSTATUS));
   memset(&counter, 0, sizeof(ARIESCOUNTER));
   memset(&inter, 0, sizeof(ARIESUSERINT));
   //memset(&dsccb,0,sizeof(DSCCB));
   memset(&Ariesfifo, 0, sizeof(ARIESFIFO));

   //
   // Initializes the DSCUD library.
   //     1. initialize the driver, using the driver version for validation
   //

   //*/
   // COMMENT ABOVE TO DISABLE INTERRUPT BASED MPE OPERATIONS

   //
   // Initialize the port_under_testboard. This function passes the various
   //      hardware parameters to the driver and resets the hardware.
   //
   //     STEPS TO FOLLOW:
   //      1. set the board type to DSC_ARIES for the ARIES board
   //      2. intialize and register the board with the driver, after which
   //        the struct, dscb, now holds the handle for the board

   dsccb.boardtype = DSC_ARIES;
   // Set the base address (Default 0x%x hit ENTER) : ",ARIES_DEFAULT_BASE_ADDRESS);
   dsccb.base_address = ARIES_DEFAULT_BASE_ADDRESS;

   // Set the IRQ (Default 0x%d hit ENTER) : ",ARIES_DEFAULT_IRQ );
   dsccb.int_level = ARIES_DEFAULT_IRQ; //5, 7, 9, 15

   if ( (ARIESInitBoard (&dsccb, &init )!= DE_NONE) )
     {
      dscGetLastError ( &errorParams );
      printf (  "ARIESInitBoard error: %s %s\n", dscGetErrorString ( errorParams.ErrCode ), errorParams.errstring );
      return -1;
     }

   bi=DSCGetBoardInfo(dsccb.boardnum);


   //Initialize Mincard (MPE) and/or any other AD system before waveform generation
   MPEdsccbp.boardtype = DSC_MPEDAQ0804;

   if ( DAQ0804InitBoard ( &MPEdsccbp ) != DE_NONE )
     {
      dscGetLastError(&errorParams);
      printf("DAQ0804InitBoard error: %s %s\n", dscGetErrorString(errorParams.ErrCode), errorParams.errstring );
      return -1;
     }

   MPEbi = DSCGetBoardInfo(MPEdsccbp.boardnum);


   //*****************************************************************************
   // AD (input) specific initialization
   //memset(&ARIESADSettings,0,sizeof(ARIESADSETTINGS));
   ARIESADSettings.Lowch = 0;
   ARIESADSettings.Highch =  numADWaveChannels - 1;

   scansize = ARIESADSettings.Highch - ARIESADSettings.Lowch + 1;

   ARIESADSettings.Polarity = 0;  // Set A/D polarity (0 for bipolar, 1 for unipolar, default: 0): " );
   ARIESADSettings.Gain = 0;   // Set A/D Gain value (0-3, 0 = 1, 1 = 2, 2 = 4, 3 = 8,default 0):");
   ARIESADSettings.Sedi = 1;   // Set input mode (0 = single-ended, 1 = differential; default 0):");
   ARIESADSettings.ScanEnable = 0;   // Set Scan Enable to false initially
   ARIESADSettings.LoadCal=1;//0;//1;

   // Continue with the scan
   if( ARIESADSettings.Lowch != ARIESADSettings.Highch )
     {
      ARIESADSettings.ScanEnable = 1;      // Set scan enable to true
      ARIESADSettings.ScanInterval = 1;      // Set scan Interval (0 = 10us, 1 = 5us, 2 = 8us, 3 = programmable, default 0):");
      //The line above is the difference between running once or running perpetually???? Does not really make sense
      //Two processes should be isolated completely on different clocks regardless of timing.
   }

   //ESSENTIAL LINE FOR GETTING THE SYSTEM TO WORK (Value 2== cntr0)
   //if ( ARIESADSetClock( bi, &ARIESADSettings.ADClk) != DE_NONE )
   /* 
   if ( ARIESADSetClock ( bi,(BYTE)2)  != DE_NONE )
      {
         dscGetLastError(&errorParams);
         printf ( "ARIESADSetClock error: %s %s\n", dscGetErrorString(errorParams.ErrCode), errorParams.errstring );
         return -1;
      }
   */
   if ( ARIESADSetClock ( bi,(BYTE)2)  != DE_NONE )
      {
         dscGetLastError(&errorParams);
         printf ( "ARIESADSetClock error: %s %s\n", dscGetErrorString(errorParams.ErrCode), errorParams.errstring );
         return -1;
      }
  //*****************************************************************************
   // DA Waveform specific initialization
   range = 0; // 0 = 0-5, 1 = 0-10, 2 = +/-5, 3 = +/-10
   //frequency = 80;

   no_channel = numDAWaveChannels;//NUM_WAVE_CHAN; //Between 1 and 4
   No_OF_DA_Channel = no_channel;
   Each_Channel_Buffer_Size = (int)(bufferSize/no_channel);

   waveform.FrameSize = no_channel;
   waveform.Frames = Each_Channel_Buffer_Size;
   waveform.Clock = CLK_SRC; // 0 = software increment, 1 = cntr0, 2 = cntr1
   waveform.Cycle = 1;
   //frequency
   rate = (float)Each_Channel_Buffer_Size * (float)waveFrequency;

   //printf("Rate: %f\n", rate);
   //printf("rate: %f", rate);
   if(rate > 250000)
       printf("invalid frequency.\n");

   //rate = 164473.0;
   //rate = 100000.0;//204800.0;
   //rate = 164473.0;//4.0;
   //rate = 10000.0;//
   //rate =float(int(rate/2));
   //The highest rate that the board can support is 164473
   waveform.Rate = rate;//frequency;


   //pause conversions if necessary
   if( ARIESWaveformPause(bi) != DE_NONE )
     {
      dscGetLastError(&errorParams);
      printf ( "ARIESWaveformStart error: %s %s\n", dscGetErrorString(errorParams.ErrCode), errorParams.errstring );
      return -1;
     }

   //in handler
   if( ARIESWaveformReset(bi) != DE_NONE )
   {
      dscGetLastError(&errorParams);
      printf ( "ARIESWaveformReset error: %s %s\n", dscGetErrorString(errorParams.ErrCode), errorParams.errstring );
      return -1;
   }


   if( ARIESWaveformConfig(bi, &waveform) != DE_NONE )
       {
          dscGetLastError(&errorParams);
          printf ( "ARIESWaveformConfig error: %s %s\n", dscGetErrorString(errorParams.ErrCode), errorParams.errstring );
          return -1;
       }

   //Allocate the memory to hold waveform values
   waveform.Waveform = (unsigned int*) malloc( (waveform.Frames * waveform.FrameSize) * sizeof(unsigned int*));
   //waveform.Waveform = new unsigned int[waveform.Frames * waveform.FrameSize];


   if( waveform.Waveform == NULL)
      {
       printf("could not allocate memory to hold waveform.\n");
       return -1;
      }

   waveform.Channels = (int *)malloc(No_OF_DA_Channel * sizeof(int *));
   //waveform.Channels = new int[No_OF_DA_Channel];
   if(waveform.Channels == NULL)
      {
       printf("could not allocate memory to hold channel values\n");
       return -1;
      }

   if( no_channel > 1)
      laserNum = 0;

   for (int channel_index = 0; channel_index < no_channel; channel_index++)
      {
       //channel = channel_index;
       waveform.Channels[channel_index] = channel_index + laserNum;
       //can be misordered or skipped around
      }

   for( int i_index = 0; i_index < bufferSize; i_index++)
      waveform.Waveform[i_index] = scanBuffer[i_index];
      //printf("Waveform val: %u, readIn: %u\n",waveform.Waveform[i_index],scanBuffer[i_index]);

   //printf("waveform.Channels[0] = %u",waveform.Channels[0]);
   for ( int i_index = 0; i_index < No_OF_DA_Channel; i_index++ )
      {
       if( ARIESDASetSettings ( bi, waveform.Channels[i_index], range, 0, 0, 1) != DE_NONE ) // channel, range, overrange, enable
         {
          dscGetLastError(&errorParams);
          printf ( "ARIESSetSettings error: %s %s\n", dscGetErrorString(errorParams.ErrCode), errorParams.errstring );
          return -1;
         }
      }

   //loads d/a conversion values into buffer
   if( ARIESWaveformBufferLoad(bi,&waveform)  != DE_NONE )
   {
      dscGetLastError(&errorParams);
      printf ( "ARIESWaveformBufferLoad error: %s %s\n", dscGetErrorString(errorParams.ErrCode), errorParams.errstring );
      return -1;
   }

   //dscSleep(5);

   //*****************************************************************************
   // AD Interrupt specific initialization
   dscIntSettings.ADClk = CLK_SRC+1; //1=ExternalTrig, 2= cntr0, 3 = cntr1
   //if (dscIntSettings.ADClk != 1)
   //    rate = frequency;


   // Load the settings into the AD system
   if ( ARIESADSetSettings ( bi,&ARIESADSettings)  != DE_NONE )
     {
      dscGetLastError(&errorParams);
      printf ( "ARIESADSetSettings error: %s %s\n", dscGetErrorString(errorParams.ErrCode), errorParams.errstring );
      return -1;
     }
   //dscIntSettings.ADClk = 0;
/*
   if( ARIESADSetClock ( bi, dscIntSettings.ADClk) != DE_NONE )
     {
      dscGetLastError(&errorParams);
      printf ( "ARIESADSetClock error: %s %s\n", dscGetErrorString(errorParams.ErrCode), errorParams.errstring );
     }
*/

   dscIntSettings.NumConversions = bufferSize;//2048;//1600; //num of A/D conversions (must be multiple of FIFO threshold value default (1600))
   dscIntSettings.Cycle = 1; //0 = one shot, 1 = continuous
   dscIntSettings.FIFOEnable = 1; //0 = disable, 1 = enable
   //if(dscIntSettings.FIFOEnable)
   //There appears to be a slight improvement when the fifo threshold matches the number of conversions
   dscIntSettings.FIFOThreshold = bufferSize;//bufferSize/4;//2048;//1600; //0-2048
   dscIntSettings.ADBuffer = (SWORD*) malloc(sizeof(SWORD)* dscIntSettings.NumConversions);
   //dscIntSettings.ADBuffer = new SWORD[dscIntSettings.NumConversions];//*2];

   if(dscIntSettings.ADBuffer == NULL)
      {
       printf("could not allocate memory for buffer\n.");
       return 0;
      }

   memset(dscIntSettings.ADBuffer, 0, (sizeof(SWORD)* dscIntSettings.NumConversions) );

   inter.IntFunc = userfun;
   inter.Mode = 2; //0 = alone, 1 = before standard function, 2 = after standard function
   inter.Enable = 1; //0 = disable interrupts, 1 = enable interrupts
   inter.Source = 0;//0; //0 = A/D, 1 = unused, 2 = counter 2, output, 4 = digital I/O

   //The SLEEP statements around this function are VERYYYY IMPORTANT for some reason
   //dscSleep(1000);
   //sleep(1);
   if( ARIESUserInterruptConfig(bi, &inter) != DE_NONE)
     {
      dscGetLastError(&errorParams);
      printf ( "ARIESUserInterruptConfig error: %s %s\n", dscGetErrorString(errorParams.ErrCode), errorParams.errstring );
      return -1;
     }
   

   //dscSleep(1000);
   //sleep(1);

   /*
   if ( ARIESADStartClock ( bi)  != DE_NONE )
     {
      dscGetLastError(&errorParams);
      printf ( "ARIESADStartClock error: %s %s\n", dscGetErrorString(errorParams.ErrCode), errorParams.errstring );
      return -1;
     }
   */

   //ARIESFIFOStatus(bi, &Ariesfifo);

   //ARIESADIntCancel(bi);


   //handler
   if ( ARIESADInt(bi, &dscIntSettings) != DE_NONE )
   {
    dscGetLastError(&errorParams);
    printf ( "ARIESADInt error: %s %s\n", dscGetErrorString(errorParams.ErrCode), errorParams.errstring );
    return -1;
   }

   //start conversions
   if( ARIESWaveformStart(bi)  != DE_NONE )
     {
      dscGetLastError(&errorParams);
      printf ( "ARIESWaveformStart error: %s %s\n", dscGetErrorString(errorParams.ErrCode), errorParams.errstring );
      return -1;
     }















   memset(&MPEdsccb, 0, sizeof(DSCCB));
   memset(&MPEdsccbp, 0, sizeof(DSCCBP));
   memset(&MPEadsettings, 0, sizeof(DAQ0804ADSETTINGS));
   memset(&MPEdscIntSettings, 0, sizeof(DAQ0804ADINT));
   memset(&MPEintstatus, 0, sizeof(DAQ0804ADINTSTATUS));
   memset(&MPECtr,0,sizeof(DAQ0804COUNTER));
   memset(&MPEinter, 0, sizeof(DAQ0804USERINT));




   MPEadsettings.Lowch = 0;
   MPEadsettings.Highch = 3;
   MPEadsettings.Polarity = 0; // 0 = Bipolar, 1 = unipolar
   MPEadsettings.Range = 0; // 0 = 5V, 1 = 10V
   MPEadsettings.Sedi = 1; // 0 = SE, 1 = DIFF
   MPEadsettings.ScanInterval = 0; // 0 = 10us, 1 = 12.5us, 2 = 20us, 3 = programmable
   //MPEadsettings.ProgInt = 0 //Only if programmable interval (range 100-255) (this value times 100ns)
   //MPEadsettings.ADClock = 0;
   MPEadsettings.ADClock = 3;//2;//2= counter 0, 3 = counter 1
   MPEadsettings.ScanEnable = 0;


   //////////////////////////////////////////////////////////////////////////
   //int MPEscansize = MPEadsettings.Highch - MPEadsettings.Lowch +1;
   MPEadsettings.ScanEnable = 0;

   if(MPEadsettings.Lowch != MPEadsettings.Highch)
   {
      MPEadsettings.ScanEnable = 1;
   }

   float MPErate = 0.0;//(int)waveFrequency * 2.0;
   if(MPEadsettings.ADClock !=1)
   {
      MPErate = waveFrequency*8.0*2.0*10.0;//10.0;//(float) ((int)waveFrequency * 2);//1000.0;
   }
   ////////////////////////////////////////////////////////////////////////////

   //If running differential, cut the range in half...

   if ( (DAQ0804ADSetSettings ( MPEbi, &MPEadsettings ) ) != DE_NONE )
   {
    dscGetLastError(&errorParams);
    printf("DAQ0804ADSetSettings error: %s %s\n", dscGetErrorString(errorParams.ErrCode), errorParams.errstring );
    return -1;
   }
/*
   if ( ( DAQ0804ADSetTiming ( MPEbi, &MPEadsettings ) ) != DE_NONE )
     {
      dscGetLastError(&errorParams);
      print("DAQ004ADSetTiming error: %s %s\n", dscGetErrorString(errorParams.ErrCode), errorParams.errstring );
      return -1;
     }
*/
   MPEDARange = 1; //0 = 0-2.5v, 1 = 0-5V
   MPEdasim = 0;
   //MPE DAQ0804 D/A Settings
   if ( DAQ0804DASetSettings( MPEbi, MPEDARange, MPEdasim ) != DE_NONE )
     {
      dscGetLastError(&errorParams);
      printf("DAQ0804DASetSettings error: %s %s\n", dscGetErrorString(errorParams.ErrCode), errorParams.errstring );
      return -1;
     }

   //COMMENT BELOW TO DISABLE INTERRUPT BASED MPE OPERATION


   MPEinter.IntFunc = MPEuserfun;
   MPEinter.Mode = 2; //0 = alone, 1 = before standard function, 2 = after standard function
   MPEinter.Enable = 1; //0 = disable interrupts, 1 = enable interrupts
   MPEinter.Source = 0; //0 = A/D, 1 = unused, 2 = counter 2, output, 4 = digital I/O

   DAQ0804UserInterruptConfig(MPEbi, &MPEinter);

   MPEdscIntSettings.NumConversions = 8;
   MPEdscIntSettings.Cycle = 1;
   MPEdscIntSettings.FIFOEnable = 1;
   //MPEdscIntSettings.ADClk = 3;
   //MPEdscIntSettings.FIFOThreshold = 8;

   if(MPEdscIntSettings.FIFOEnable)
       MPEdscIntSettings.FIFOThreshold = 8;//MPEdscIntSettings.NumConversions;//1000;

   MPEdscIntSettings.ADBuffer = (SWORD*) malloc (sizeof(SWORD)* MPEdscIntSettings.NumConversions );
   //MPEdscIntSettings.ADBuffer = new SWORD[MPEdscIntSettings.NumConversions];

   if(MPEdscIntSettings.ADBuffer == NULL)
   {
      printf("Could not allocate memory for ADBuffer \n");
      return -1;
   }
   if( DAQ0804ADInt(MPEbi,&MPEdscIntSettings ) !=DE_NONE)
   {
       dscGetLastError(&errorParams);
       printf ( "DAQ0804ADInt error: %s %s\n", dscGetErrorString(errorParams.ErrCode), errorParams.errstring );
       return -1;
   }

   if(MPEadsettings.ADClock !=1)
   {
       MPECtr.Rate = MPErate ;
       MPECtr.CtrNo = MPEadsettings.ADClock-2 ;
       MPECtr.CtrClk = 3;//2;//3; Clk2 is 50MHz?
       MPECtr.CtrOutEn 	= 0 ;
       MPECtr.CtrOutPol = 0 ;
       MPECtr.ctrOutWidth = 0 ;

       if( DAQ0804CounterSetRate(MPEbi,&MPECtr) !=DE_NONE)
       {
           dscGetLastError(&errorParams);
           printf ( "DAQ0804ADInt error: %s %s\n", dscGetErrorString(errorParams.ErrCode), errorParams.errstring );
           return -1;
       }
   }

   if ( (DAQ0804ADSetTiming(MPEbi,&MPEadsettings) ) != DE_NONE )
   {
           dscGetLastError(&errorParams);
           printf ( "DAQ0804ADSetTiming error: %s %s\n", dscGetErrorString(errorParams.ErrCode), errorParams.errstring );
           return -1;
   }
    //dscSleep(1000);
   //ARIESADIntResume(bi);


   return 0;
  }


int statusMPE( void )
  {
   /*
   if( DAQ0804ADIntStatus(MPEbi, &MPEintstatus) != DE_NONE )
     {
      dscGetLastError(&errorParams);
      printf("DAQ0804ADIntStatus error: %s %s\n", dscGetErrorString(errorParams.ErrCode), errorParams.errstring);
     }
   return (int)MPEintstatus.NumConversions;
   */
   return (int)MPEcounter;
  }


void writeMPEvoltage( float voltage , int channel)
  {
   if ( voltage > MPEVrefs[MPEDARange] || voltage < 0 )
      return;
   DACode = (unsigned long int) (voltage/MPEVrefs[MPEDARange] * 2.0 * 65535.0);
   //Expected = (double)(DACode/65535.0) * MPEVrefs[MPEDARange];
   if ( ( DAQ0804DAConvert ( MPEbi, channel, DACode ) ) != DE_NONE )
     {
      dscGetLastError(&errorParams);
      printf("DAQ0804DASetSettings error: %s %s\n", dscGetErrorString(errorParams.ErrCode), errorParams.errstring );
      return;
     }
  }

void MPEreadBuffer( int *voltage )
  {
   for(int i_index = 0; i_index < 8; i_index++ )//MPEdscIntSettings.NumConversions; i_index++)
      voltage[i_index] = MPEdscIntSettings.ADBuffer[i_index];
  }

void MPEanalogConvert( float *voltage )
  {
   for(int i_index = 0; i_index <= MPEadsettings.Highch - MPEadsettings.Lowch; i_index++)
     {
      if(MPEadsettings.Polarity == 0)
         voltage[i_index] = (float)(voltage[i_index]/65536.0) * MPEVrefsBip[MPEadsettings.Range];
      else
         voltage[i_index] = (float)((voltage[i_index] + 32768)/65536.0) *MPEVrefs[MPEadsettings.Range];
     }
  }


int analogIntStatus()// int lastCount )
  {
   if ( ARIESFIFOStatus(bi, &Ariesfifo) != DE_NONE)//;
     {
      dscGetLastError (&errorParams);
      printf ( "ARIESFIFOStatuserror: %s %s\n",
        dscGetErrorString(errorParams.ErrCode),
        errorParams.errstring);
      return 0;
     }
   //if ( Ariesfifo.Depth == 2048 ) 
   //  {
   //   count++;
   //  }
   return (int)Ariesfifo.EF;//total_transfers;//count;
  }


int readBuffer( int *voltage )
  {
   short int sample;
   for ( int i_index = 0; i_index < dscIntSettings.NumConversions; i_index++)
      voltage[i_index] = dscIntSettings.ADBuffer[i_index];
   return count;
  }

int readBufferVoltage( float *voltage )
  {
   double outputVoltage = 0.00;
   for(int i_index = ARIESADSettings.Lowch, j_index = 0; j_index < dscIntSettings.NumConversions; i_index++, j_index++)
     {
      if(ARIESADSettings.Polarity == 0)
         outputVoltage = (float)(dscIntSettings.ADBuffer[j_index]/65536.0) * VrefsBip[ARIESADSettings.Gain];
      else
         outputVoltage = (float)((dscIntSettings.ADBuffer[j_index] + 32768)/65536.0) *VrefsAD[ARIESADSettings.Gain];
      voltage[j_index] = outputVoltage;
     }
   return (int)(count);//(intstatus.NumConversions);
  }

void analogConvert( float *voltage )
  {
   for(int i_index = ARIESADSettings.Lowch, j_index = 0; j_index < dscIntSettings.NumConversions; i_index++, j_index++)
     {
      if(ARIESADSettings.Polarity == 0)
         voltage[j_index] = (float)(voltage[j_index]/65536.0) * VrefsBip[ARIESADSettings.Gain];
      else
         voltage[j_index] = (float)((voltage[j_index] + 32768)/65536.0) *VrefsAD[ARIESADSettings.Gain];
     }
  }
//Remnant comment section that needs to be added to other codes
//=========================================================================
// Scan all 16 channels to read analog channels
//
//     Perform the actual sampling and output the results. To calculate
//      the actual input voltages, we must convert the sample code (which
//      must be cast to a short to get the correct code) and then plug it
//      into one of the formulas located in the manual for your board (under
//      "A/D Conversion Formulas").
//=========================================================================
/*

/*********************************************************************/
// Cleanup any remnants left by the program and free the resources used
// by the driver.
/*********************************************************************/

int interface_close(void) {

   for( int i = 0; i < (int)(waveform.Frames * waveform.FrameSize); i++ )
      waveform.Waveform[i] = 0;//waveform_value;


   //start conversions
   if( ARIESWaveformPause(bi) != DE_NONE )
     {
      dscGetLastError(&errorParams);
      printf ( "ARIESWaveformStart error: %s %s\n", dscGetErrorString(errorParams.ErrCode), errorParams.errstring );
      return -1;
     }

   if( ARIESWaveformBufferLoad(bi,&waveform)  != DE_NONE )
   {
      dscGetLastError(&errorParams);
      printf ( "ARIESWaveformBufferLoad error: %s %s\n", dscGetErrorString(errorParams.ErrCode), errorParams.errstring );
      return -1;
   }

   //dscSleep(1000);

   //start conversions
   if( ARIESWaveformPause(bi) != DE_NONE )
     {
      dscGetLastError(&errorParams);
      printf ( "ARIESWaveformStart error: %s %s\n", dscGetErrorString(errorParams.ErrCode), errorParams.errstring );
      return -1;
     }

   //in handler
   if( ARIESWaveformReset(bi) != DE_NONE )
   {
      dscGetLastError(&errorParams);
      printf ( "ARIESWaveformReset error: %s %s\n", dscGetErrorString(errorParams.ErrCode), errorParams.errstring );
      return -1;
   }

   //dscSleep(1000);
   free(waveform.Waveform);
   free(waveform.Channels);
   //delete[] waveform.Waveform;
   //delete[] waveform.Channels;
   
   //ARIESADIntPause(bi);
   ARIESADIntCancel(bi);
   DAQ0804ADIntCancel(MPEbi);


   free(dscIntSettings.ADBuffer);
   free(MPEdscIntSettings.ADBuffer);
   //delete[] dscIntSettings.ADBuffer;
   //delete[] MPEdscIntSettings.ADBuffer;

   //ARIESCounterReset(bi,  dscIntSettings.ADClk - 2);
   //ARIESCounterReset(bi, 0);
   //ARIESCounterReset(bi, 1);
   //ARIESCounterReset(bi, 2);

   ARIESADStopClock(bi);
   for( int i = 0; i < 8; i++ )
       ARIESCounterReset(bi,i);

   ARIESFreeBoard(dsccb.boardnum);
   DAQ0804FreeBoard(MPEdsccbp.boardnum);
   //DAQ0804FreeBoard(MPEdscb);
   dscFree ( );

   printf("Successful Shutdown\n");
   return 0;
}

