//=============================================================================
// (c) Copyright 2014 Diamond Systems Corporation. Use of this source code
// is subject to the terms of Diamond Systems' Software License Agreement.
// Diamond Systems provides no warranty of proper performance if this
// source code is modified.
//
// File: ARIES ADSample.c   v1.00 VEGA
//
// Dependency :	Universal Driver version 7.00
//				DSCUD.H - Include file.
//				
//				LIBDSCUD-7.00.a	- Library file for Linux 2.6.29-3.x
//						
//				DSCUD.LIB	- Static library file for Windows 
//						( USE VC++ 6.0 or Visual Studio 2005 )
// 
// Description: This sample code demonstrates the usage of UD function
//				ARIESADSample(). This sample code describes the usage
//				for ARIES board. An A/D Sample will be taken from the
//              on board hardware, and transferred to a value in user space;
//              this value will then be interpreted based on the mode
//              that the user set.
//
//=============================================================================


#include "DSCUD_demo_def.h"
#include "Aries.h"
#define ARIES_DEFAULT_BASE_ADDRESS 0x280
#define ARIES_DEFAULT_IRQ 5

// var declarations
BYTE result;  // returned error code
DSCB dscb;    // handle used to refer to the board
DSCCB dsccb; // structure containing board settings 
ARIESADSETTINGS dscadsettings; // structure containing A/D conversion settings
ARIESADINT	 dscIntSettings;//  structure containing A/D conversion interrupt settings
ARIESADINTSTATUS intstatus;// structure containing A/D conversion interrupt status
ARIESINIT Init;
ARIESCOUNTER counter;
float rate;

ERRPARAMS errorParams;  // structure for returning error code and error string
int intBuff;            // temp variable of size int
DFLOAT voltage;
int i;	// miscellaneous counter
SWORD sample;
char input_buffer[20]; // Buffer for parsing user character input.
int channel=0;

BoardInfo *bi;

//=============================================================================
// Name: main()
// Desc: Starting function that calls the driver functions used
//
//		 NOTE: By convention, you should capture the BYTE return value for each
//		 driver API call, and check the error code.
//
//	     I. Driver Initialization
//	    II. Board Initialization
//	   III. AD Settings
//	    IV. IO Settings
//		 V. Sample
//	    VI. Cleanup
//
//=============================================================================

int main()
{
	double Vrefs[4]={10.0,5.0,2.5,1.25};
	double VrefsBip[4]={20.0,10.0,5.0,2.5};
	double outputVoltage = 0.0;
	int key = 0;
	int Pause = 0 ,iindex = 0 , jIndex ;
	memset(&dscadsettings,0,sizeof(ARIESADSETTINGS));
	//=========================================================================
	// I. DRIVER INITIALIZATION
	//
	//    Initializes the DSCUD library.
	//
	//=========================================================================

	if ( dscInit ( DSC_VERSION ) != DE_NONE )
	{
		dscGetLastError(&errorParams);
		printf ("dscInit error: %s %s\n", dscGetErrorString(errorParams.ErrCode), errorParams.errstring );
		return 0;
	}

	//=========================================================================
	// II. BOARD INITIALIZATION
	//
	//	   Initialize the ARIES board. This function passes the various
	//	   hardware parameters to the driver and resets the hardware.
	//
	//=========================================================================

	dsccb.boardtype = DSC_ARIES;
	// The ARIES has a fixed base address.
	//dsccb.base_address = 0x280;
	//dsccb.int_level = 5;

	printf ( "Enter the base address (Default 0x%X hit ENTER) : ",ARIES_DEFAULT_BASE_ADDRESS );
	fgets ( input_buffer, 20, stdin );
	if ( input_buffer[0] == '\n' )
	{
	   dsccb.base_address = ARIES_DEFAULT_BASE_ADDRESS;
	}
	else
	{
	   sscanf(input_buffer,"%hx",&dsccb.base_address);
	}
	
	printf ( "Enter the IRQ (Default 0x%d hit ENTER) : ",ARIES_DEFAULT_IRQ );
	fgets ( input_buffer, 20, stdin );
	if ( input_buffer[0] == '\n' )
	{
	   dsccb.int_level = ARIES_DEFAULT_IRQ;
	}
	else
	{
	   sscanf(input_buffer,"%d",&dsccb.int_level);
	}

	if ( ARIESInitBoard ( &dsccb,&Init) != DE_NONE )
	{
		dscGetLastError(&errorParams);
		printf("ARIESInitBoard error: %s %s\n", dscGetErrorString(errorParams.ErrCode), errorParams.errstring );
		return 0;
	}
	bi=DSCGetBoardInfo(dsccb.boardnum);
	printf("\nARIES AD SAMPLE FUNCTION DEMO\n");
	//=========================================================================
	// III. SAMPLING AND OUTPUT
	//
	//     Perform the actual sampling and output the results. To calculate
	//	   the actual input voltages, we must convert the sample code (which
	//	   must be cast to a short to get the correct code) and then plug it
	//	   into one of the formulas located in the manual for your board (under
	//	   "A/D Conversion Formulas").
	//=========================================================================
	
	do
	{
		memset(&dscadsettings,0,sizeof(ARIESADSETTINGS));
		memset(&dscIntSettings, 0, sizeof(ARIESADINT));
		memset(&intstatus, 0, sizeof(ARIESADINTSTATUS));
		memset(&counter, 0, sizeof(ARIESCOUNTER));
		
		printf("Enter channel number(0-15,default:0)");
		fgets ( input_buffer, 20, stdin );
		if ( input_buffer[0] == '\n' )
		{
			channel=0;
		}
		else
		{
			sscanf ( input_buffer, "%d", &channel );
			 
		}
		
		printf ( "Enter A/D polarity (0 for bipolar, 1 for unipolar, default: 0): " );
		fgets ( input_buffer, 20, stdin );
		if ( input_buffer[0] == '\n' )
		{
			dscadsettings.Polarity = 0;
		}
		else
		{
			sscanf ( input_buffer, "%d", &dscadsettings.Polarity );
			 
		}

		printf("Enter A/D Gain value (0-3, 0 = 1, 1 = 2, 2 = 4, 3 = 8,default 0):");
		fgets ( input_buffer, 20, stdin );
		if ( input_buffer[0] == '\n' )
		{
			dscadsettings.Gain = 0;
		}
		else
		{
			sscanf ( input_buffer, "%d", &dscadsettings.Gain );
			
		}
		
		printf("Enter input mode (0 = single-ended, 1 = differential; default 0):");
		fgets ( input_buffer, 20, stdin );
		if ( input_buffer[0] == '\n' )
		{
			dscadsettings.Sedi = 0;
		}
		else
		{
			sscanf ( input_buffer, "%d", &dscadsettings.Sedi );
			
		}
		dscadsettings.Highch = channel;
		dscadsettings.Lowch = channel;
		dscadsettings.ScanEnable = 0;
		//dscadsettings.LoadCal = 0;//changed
		printf("Load calibration values  (0 = No, 1 = Yes; default 1):");
		fgets ( input_buffer, 20, stdin );
		if ( input_buffer[0] == '\n' )
		{
			dscadsettings.LoadCal = 1;
		}
		else
		{
			sscanf ( input_buffer, "%d", &dscadsettings.LoadCal );
			
		}
		
		printf("Enter Clock source (0-3; 0 = Manual, 1= External trigger, 2=Counter 0, 3=Counter 1, default=0):");
		fgets ( input_buffer, 20, stdin );
		if ( input_buffer[0] == '\n' )
		{
			dscIntSettings.ADClk = 0;
		}
		else
		{
			sscanf ( input_buffer, "%d", &dscIntSettings.ADClk );
			
		}	
		
		if(dscIntSettings.ADClk == 0)				
		{
			if ( ARIESADSetSettings ( bi,&dscadsettings)  != DE_NONE )
			{
				dscGetLastError(&errorParams);
				printf ( "ARIESADSetSettings error: %s %s\n", dscGetErrorString(errorParams.ErrCode), errorParams.errstring );
				return 0;
			}
			
			if ( ARIESADSetClock ( bi,dscIntSettings.ADClk)  != DE_NONE )
			{
				dscGetLastError(&errorParams);
				printf ( "ARIESADSetClock error: %s %s\n", dscGetErrorString(errorParams.ErrCode), errorParams.errstring );
				return 0;
			}
			
			if ( ARIESADStartClock ( bi)  != DE_NONE )
			{
				dscGetLastError(&errorParams);
				printf ( "ARIESADStartClock error: %s %s\n", dscGetErrorString(errorParams.ErrCode), errorParams.errstring );
				return 0;
			}
			printf("Press Enter key to stop A/D sampling\n");
			printf("\nChannel Num\tA/DValue(Dec)\tA/DValue(Hex)\tVolts\n\n");
			while (!kbhit() )
			{
			
				if ( ARIESADSample ( bi,&sample)  != DE_NONE )
				{
					dscGetLastError(&errorParams);
					printf ( "ARIESADSample error: %s %s\n", dscGetErrorString(errorParams.ErrCode), errorParams.errstring );
					return 0;
				}
			
				if(dscadsettings.Polarity == 0)
				{
					outputVoltage =	(double)((sample)/65536.0)* VrefsBip[dscadsettings.Gain];
					//outputVoltage =	(double)((sample-32768)/32768.0)*Vrefs[dscadsettings.Gain];
				}
				else
				{
					outputVoltage =	(double)((sample+32768)/65536.0)* Vrefs[dscadsettings.Gain];
					//outputVoltage =	(double)((sample)/65535.0)*Vrefs[dscadsettings.Gain];
				}

			
				
			printf("%2d\t\t%d\t\t0x%X\t\t%0.4lf\n",channel,sample,(unsigned short)sample,outputVoltage);
			dscSleep(1000);			
			
			}
		}
		else
		{
			if(dscIntSettings.ADClk !=1)
			{
				printf("Enter A/D sampling Rate (Default 1000) :" );
				fgets ( input_buffer, 20, stdin );
				if ( input_buffer[0] == '\n' )
				{
					rate =1000.0;
				}
				else
				{
					sscanf ( input_buffer, "%f", &rate );			 
				}
			}
			
			if ( ARIESADSetSettings ( bi,&dscadsettings)  != DE_NONE )
			{
				dscGetLastError(&errorParams);
				printf ( "ARIESADSetSettings error: %s %s\n", dscGetErrorString(errorParams.ErrCode), errorParams.errstring );
				return 0;
			}
			
			if ( ARIESADSetClock ( bi,dscIntSettings.ADClk)  != DE_NONE )
			{
				dscGetLastError(&errorParams);
				printf ( "ARIESADSetClock error: %s %s\n", dscGetErrorString(errorParams.ErrCode), errorParams.errstring );
				return 0;
			}
			
			printf ("Enter number of A/D conversions (must be multiple of FIFO threshold value default 1000): " );
			fgets ( input_buffer, 20, stdin );
			if ( input_buffer[0] == '\n' )
			{
				dscIntSettings.NumConversions = 1000;
			}
			else
			{
				sscanf ( input_buffer, "%d", &dscIntSettings.NumConversions );
			}
			
			printf ( "Enter the cycle flag (0 = one shot operation, 1 = continuous operation, default: 1) : " );
			fgets ( input_buffer, 20, stdin );
			if ( input_buffer[0] == '\n' )
			{
				dscIntSettings.Cycle = 1;
			}
			else
			{
				sscanf ( input_buffer, "%d", &dscIntSettings.Cycle );
			}
			
			printf ( "Enter FIFO Enable bit value (0 = disable, 1 = enable, default: 1) : " );
			fgets ( input_buffer, 20, stdin );
			if ( input_buffer[0] == '\n' )
			{
				dscIntSettings.FIFOEnable = 1;
			}
			else
			{
				sscanf ( input_buffer, "%d", &dscIntSettings.FIFOEnable );
			}
			
			if(dscIntSettings.FIFOEnable)
			{
				
				printf ( "Enter FIFO Threshold value (0-2048  default: 1000) : " );
				fgets ( input_buffer, 20, stdin );
				if ( input_buffer[0] == '\n' )
				{
					dscIntSettings.FIFOThreshold = 1000;
				}
				else
				{
					sscanf ( input_buffer, "%d", &dscIntSettings.FIFOThreshold );
				}
				
			}
		
			dscIntSettings.ADBuffer = (SWORD*) malloc (sizeof(SWORD)* dscIntSettings.NumConversions );
		
			if(dscIntSettings.ADBuffer == NULL)
			{
			   printf("Could not allocate memory for ADBuffer \n");
			   return 0;
			}
			memset(dscIntSettings.ADBuffer,0,(sizeof(SWORD)* dscIntSettings.NumConversions) );
				
			if( ARIESADInt(bi,&dscIntSettings ) !=DE_NONE)
			{
				dscGetLastError(&errorParams);
				printf ( "DAQ0804ADInt error: %s %s\n", dscGetErrorString(errorParams.ErrCode), errorParams.errstring );
				return 0;
			}
		
			if(dscIntSettings.ADClk !=1)
			{
				counter.CtrNo = dscIntSettings.ADClk-2 ;
				counter.Rate = rate ;
				counter.CtrOutEn = 0 ;
				counter.CtrOutPol =  0;
				counter.ctrOutWidth  = 0;
				if(ARIESCounterSetRate(bi,&counter) !=DE_NONE)
				{
					dscGetLastError(&errorParams);
					printf("ARIESCounterSetRate error: %s %s\n", dscGetErrorString(errorParams.ErrCode), errorParams.errstring );	
					return 0;
				}
			}
				
			dscSleep(1000);
			printf("\nPress Space bar key to Pause/Resume A/D Int or Press any other key to stop A/D Interrupt \n");
			
			while( 1 )
			{
				key = kbhit();
				if(key==0)
				{
					if(ARIESADIntStatus(bi,&intstatus) !=DE_NONE)
					{
						dscGetLastError(&errorParams);
						printf ( "ARIESADIntStatus error: %s %s\n", dscGetErrorString(errorParams.ErrCode), errorParams.errstring );
						return 0;
					}
				
				
					printf("No of A/D conversions completed %d\n",intstatus.NumConversions);
														
					dscSleep(1000);
					if( (dscIntSettings.Cycle == 0) && (intstatus.NumConversions >=dscIntSettings.NumConversions) ) break;

				}
				else
				{
						 key = getch();//ar();
						 if(key ==32 )
						{
							if(Pause )
							{
								//printf("Resume function called \n");
								if(ARIESADIntResume(bi) !=DE_NONE)
								{
									dscGetLastError(&errorParams);
									printf ( "ARIESADIntResume error: %s %s\n", dscGetErrorString(errorParams.ErrCode), errorParams.errstring );
									return 0;
								}
								Pause = 0;
							}
							else
							{
								//printf("Pause function called \n");
								if(ARIESADIntPause(bi) !=DE_NONE)
								{
									dscGetLastError(&errorParams);
									printf ( "ARIESADIntPause error: %s %s\n", dscGetErrorString(errorParams.ErrCode), errorParams.errstring );
									return 0;
								}

								Pause = 1 ;
							}
						}
						else
						{
							break;
						}
				}
							
						
				
			}
			/*
			#ifdef _WIN32
			fgets(input_buffer,20,stdin);
			#endif	.
			*/
			printf("\nChannel Num\tA/DValue(Dec)\tA/DValue(Hex)\tVolts\n\n");
			for(iindex= dscadsettings.Lowch,jIndex=0; iindex <= dscadsettings.Highch && jIndex </*scansize*/1; iindex++,jIndex++)
			{

				if(dscadsettings.Polarity == 0)
				{
					outputVoltage =	(double)(dscIntSettings.ADBuffer[jIndex]/65536.0)* VrefsBip[dscadsettings.Gain];
				}
				else
				{
					outputVoltage =	(double)( (dscIntSettings.ADBuffer[jIndex] + 32768) /65536.0)* Vrefs[dscadsettings.Gain];
				}
				printf("%2d\t\t%d\t\t0x%X\t\t%0.4lf\n",iindex,dscIntSettings.ADBuffer[jIndex],(unsigned short)dscIntSettings.ADBuffer[jIndex], outputVoltage);							
			}
			printf("\n\n");
			/*printf("Press Enter to repeat or 'q' to quit \n");
			fgets(input_buffer,20,stdin);
			*/ARIESADIntCancel(bi);
			free(dscIntSettings.ADBuffer);
			if(dscIntSettings.ADClk !=1)
			{
				if( ARIESCounterReset(bi,dscIntSettings.ADClk-2 ) !=DE_NONE)
				{
					dscGetLastError ( &errorParams );
					printf ( "ARIESCounterReset error: %s %s\n", dscGetErrorString ( errorParams.ErrCode ), 				errorParams.errstring);		
					return 0;
				}
			}
				
		
		}
		
		fgets(input_buffer,20,stdin);
		printf ("press Enter to repeat or 'q' to quit:");
   		fgets ( input_buffer, 20, stdin );

    } while ( input_buffer[0] != 'q' );


	//=========================================================================
	// V. CLEANUP
	//
	//	  Cleanup any remnants left by the program and free the resources used
	//	  by the driver.
	//
	//    STEPS TO FOLLOW:
	//
	//	  1. free the driver resources
	//====================================================================

	dscFree();

	

	printf ( "\nARIESADSample completed.\n" );

	return 0;
} // end main()


#ifdef _WIN32_WCE
int WINAPI WinMain(	HINSTANCE hInstance,
					HINSTANCE hPrevInstance,
					LPTSTR    lpCmdLine,
					int       nCmdShow)
{
	main();

	return 0;
}

#endif
