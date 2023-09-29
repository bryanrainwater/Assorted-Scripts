
// diamond driver includes
#include "dscud.h"
#include "stdio.h"
#include "string.h"
#include "stdlib.h"
#include "stdint.h"
#include "time.h"
#include "sys/time.h"
#include "math.h"
#include "errno.h"
#include "sys/stat.h"
#include "sys/statvfs.h"
#include "signal.h"
#include "sys/socket.h"
#include "arpa/inet.h"
#include "unistd.h"

#include "inttypes.h"


// Analog Output channel definitions 
#define VOUTCH_MFC    0
#define VOUTCH_LASER  1

#define VOUTCH_SETPT  2
// Analog Input channel definitions
#define VINCH_DETECTD 0 
#define VINCH_SENSED  1 
#define VINCH_TDETECT 2 
#define VINCH_TLASER  3 
#define VINCH_RTD1    4 
#define VINCH_RTD3    5 
#define VINCH_RTD2    6 
#define VINCH_PRESS   7 
#define VINCH_LSRCURR 8 
#define VINCH_LSRVOLT 9 
#define VINCH_DETECTS 10
#define VINCH_SENSES  11
#define VINCH_MFC     12
#define HK_CH_START   1  // First sequential channel to scan in HK A/D conversion
#define HK_CH_END     12 //  Last sequential channel to scan in HK A/D conversion
#define HKPTS	      HK_CH_END - HK_CH_START + 1 // number of housekeeping channels

// Define general operating parameters
#define MFCSCALE          0.5f // = (MFC setpoint volts) / (MFC SLM)
#define PI                3.14159265f // Everybody loves pi!
#define CHARLENGTH	  100 // size of filename char arrays
#define MIN_DISK_CAPACITY 300 // minimum free disk space to maintain (in MB)

// Define scan operational parameters
//#define SCANPTS           512 // # points in scan ramp  
#define SCANPTS		  1024
#define DA_CH_PER_FRAME   1 // (1-4: # values to output per trigger)
#define DA_CLK_SOURCE     2 // trigger clock source: 1=Ctr0, 2=Ctr1&2
//#define DA_OUTRATE        32768 // point Hz, not scan Hz
//#define DA_OUTRATE        65536 // point Hz, not scan Hz
#define DA_OUTRATE        250000//245760//247760//16384//196608//65536
//#define DARKINTERVAL      40 // # pts in dark count (of SCAN_PTS total)
#define DARKINTERVAL      128 // # pts in dark count (of SCAN_PTS total)
//#define DARANGE           4096 // full scale D/A output (counts 2^16)
#define DARANGE		  65536
#define DAVOLTS           5.0f // full scale D/A output in volts
#define HK_NSAMPLES       5 // (<32665) # of samples of each HK channel to average
//#define HK_NSAMPLES       1 // (<32665) # of samples of each HK channel to average
//#define SC_NSAMPLES	  15 // # of DC scans to average to produce each saved
#define SC_NSAMPLES	  50//1//50 // # of DC scans to average to produce each saved
//#define SC_PER_HK	  3 // # of DC scans between HK reads
#define SC_PER_HK	  4//240000//4 // # of DC scans between HK reads
//Add changed the above SC_PER_HK from default 5 to 101 for temperature scan!!

#define SLEEP_MS 	  0 // (millisec) pause duration during DC interrupt scan

//Use PP2F?
#define USE_PP2F	  0


// pp2f-specific setting
#define PP_NSAMPLES	  1 // # of pp2f scans to average to produce each saved
#define PPWAVEPTS         16.0f // (>4) # DC scan points per sine wavelength
#define PPRAMPSEGS	  5 // # sequential SCANPTS ramps to make 1 pp2f ramp
#define PP_PER_HK	  101 // # of pp2f scans between HK reads
#define PPSCANPTS  	  SCANPTS * PPRAMPSEGS // # points in multi-segment pp2f scan ramp

//New definitions for temperature ramping:
#define STARTSETPT	  600.0
#define ENDSETPT	  1000.0
#define TEMP_SCAN	  0 //Change to 1 to allow temperature scan according to above parameters
//Also change SC_PER_HK parameter above to determine the number of divisions in temp range.

//Define configuration limits
//#define LASERVMAX         4.5
#define LASERVMAX	  5.0
#define MINMFC            0.0
#define MAXMFC            5.0
#define MINVSTART         0.0
#define MAXVSTART         5.0
#define MINVEND           0.0
#define MAXVEND           5.0
#define MINVMOD           0.0
#define MAXVMOD           5.0
#define MINMINSPERFILE    1
#define MAXMINSPERFILE    1000
#define PP2FDEFAULT       0 // If invalid entry in param file for pp2f enable, default to 'off'


//Definitions for Gnu Plotting
#define NUM_POINTS 5
#define NUM_COMMANDS 2


#define BILLION 1000000000L

static int kbhit()
{
    struct timeval timeout;
    fd_set rfds;

    timeout.tv_sec = 0;
    timeout.tv_usec = 0;

    FD_ZERO(&rfds);
    FD_SET(0, &rfds);

    if ( select(0+1, &rfds, NULL, NULL, &timeout) > 0 )
      return getchar();

    return 0;
}                                                                                                                                                              

struct CONFIG
{
  float MFC;
  float vStart;
  float vEnd;
  float vMod;
  float LSetPt; //Modified for Arduino Set Point
  int pp2fEnable;
  int minsPerFile;
  int verbose;
  int sendUDP;
};

// Variable declarations
char activeFileRef[CHARLENGTH] = "/home/dscguest/clh2ops/activeFilename.txt";
char ConfigFile[CHARLENGTH] = "/home/dscguest/clh2ops/configCLH2.txt";
char StartLogFile[CHARLENGTH] = "/home/dscguest/clh2ops/startLog.txt";
char OutputFile[CHARLENGTH];
char timestamp[CHARLENGTH];
char UDPtime[CHARLENGTH];
FILE *ptr_HKfile; // pointer to housekeeping file
FILE *ptr_SCfile; // pointer to housekeeping file
int DCscanRamp[SCANPTS]; // DC scan ramp is single scan
int ACscanRamp[SCANPTS * PPRAMPSEGS]; // pp2f ramp built of several segments
BYTE result; // returned error code
DSCB dscb;  // handle used to refer to the board
DSCCB dsccb; // structure containing board settings
DSCADSETTINGS dscadsettings; // structure containing A/D conversion settings
DSCDASETTINGS dscdasettings; // structure containing D/A conversion settings
DSCADSCAN dscadscan; // Structure containing A/D scan settings
DSCSAMPLE* HKsamples; // HouseKeeping sample readings
DSCS dscs;  // structure containing interrupt-based sampling status information
DSCAIOINT dscaioint;  // structure containing interrupt-based sampling settings
DSCWGCONFIG dscWGconfig; // structure containing waveform generation configuration
ERRPARAMS errorParams; // structure for returning error code and error string
DFLOAT voltage; // Buffer for holding calculated floats

DSCCR dsccr; //Counter Reading Settings
//DSCUSERINTFUNCTION dscuserintfunction;


float HKvolts[HKPTS + 1]; // Array for assembling calibrated voltages for preflight output
float VMRraw; // variable to contain quanity sensitive to VMR
float pres; // variable to contain approximate cell pressure
float temp;
float rendpt;

float therr; //temperature of herriott cell

int preflightFlag = 0; // Command line flag for displaying preflight diagnostics
int HKaccum[HKPTS]; // accumulator array for HK variables
int SCaccum[SCANPTS]; //accumulator array for SC input
float realscan[SCANPTS];
float normalize[SCANPTS];
int i;       // miscellaneous index counter
int i_sample_count; // index # scans written per HK 
int i_sample_avg; // index # scans collected to average per scan write
int intBuff; 	 // temporary variable with type int
long longBuff; 	 // temporary variable with type long
float floatBuff; // temporary variable with type float
time_t secondsUNIX; // seconds since UNIX epoch (Jan 1, 1970)
time_t fileStart_secondsUNIX; // at file initialization, seconds since UNIX epoch
struct timeval tv,tv1,tv2;//Added tv1 and tv2 to interpolate time of measurement.
struct CONFIG config; // parameters from config text file
struct CONFIG config =
  {
    0.0F,
    0.0F,
    0.0F,
    0.0F,
    0.0F, //Modified for Arduino Set Point
    0,
    0,
    0
  }; 

//clock_t WGStartTime;
//clock_t WGCurrentTime;

struct timespec WGStartTime,WGCurrentTime;
float WGelapsed;
int WGindex;


// Declare names of channels, simply for comprehensible output in verbose modes
char* channame[] = { "DetectD", "SenseD", "TDetect", "TLaser", "CellTemp1", "PlateTemp", "CellTemp2", 
        "Pressure", "LCurrent", "LVoltage", "DetectS", "SenseS", "MFC" };

// Function declarations
int readConfig();
int checkConfig();
int getOutputFilename();
int initHKfile();
int initSCfile();
void createACScanRamp();
void createDCScanRamp();
void startWGInterrupt();
int DMMinit();
void handleInterrupt( int sig );
void prepareToExit();
int setMFC( float );
int setSetPt( float ); //New prototype for Arduino set point
int ACscan();
int DCscan();
int getHK();
int checkChunk();
int checkDisk();
int autoCal();
double getFreeDiskSpace();




/////////////////////////////////////////////////////
////////////// Function definitions /////////////////
/////////////////////////////////////////////////////

double getFreeDiskSpace() {
	// Checks disk space remaining locally, returns in MB
	unsigned long long diskFree = 0;
	struct statvfs fInfo;
	double f_cap = -1;
	
	if ( statvfs( "/", &fInfo) != -1 )  // check for error
	{
	        //  printf("%lu  %lu\n", fInfo.f_bsize, fInfo.f_bfree);
		// Free space is # blocks free * block size (bytes)
		diskFree = (unsigned long long)fInfo.f_bsize * fInfo.f_bfree;
		f_cap = (double)diskFree/(1024*1024); // Convert to MB
	}
	return f_cap;
}

int checkDisk() {
	// Checks remaining disk space and prevents overwriting if disk 
	// nears capacity set in MIN_DISK_CAPACITY define statement.
	if ( getFreeDiskSpace() < MIN_DISK_CAPACITY ) 
	{
		printf("Disk is at capacity!!  No more data will be written");
		prepareToExit();
                exit(EXIT_SUCCESS);
		return 0;
	}
	return 1;
}

int checkChunk() {
	// In order to reduce the risk of data loss from hard powerdowns
	// or other file corruption, we limit the duration of data written
	// to each file.  The time duration is a configurable parameter in
	// the configCLH2.txt file.
	//
	// This function checks if the current output files contain
	// the specified duration of data.  If so, the current files are
	// closed and new files are created.
	
	secondsUNIX = time( NULL );
	
	// If specified duration is met or exceeded
	if( ( (int)secondsUNIX - (int)fileStart_secondsUNIX ) >= ( config.minsPerFile * 60) )
	{
		fclose(ptr_HKfile); // Close existing files
		fclose(ptr_SCfile);
		
		getOutputFilename(); // Get new filename
		initHKfile(); // Create and initialize new files
		initSCfile();
		
		// Period autocalibration is disabled, since it caused 20 second gaps in data
		// Repeat auto-calibration
		//if( (result = autoCal()) == 0 )
        //        {
        //          fprintf( stderr, "dsc Auto Calibration error.");
        //          return 0;
        //        }  
	}
	return 1;
}

int getHK() {

/*
  // Set all analog-to-digital configuration values to zero
  memset(&dscadsettings, 0, sizeof(DSCADSETTINGS));


  // Define new A/D configuration for HK operations
//  dscadsettings.range = RANGE_10;
  dscadsettings.range = RANGE_5;
//  dscadsettings.polarity = UNIPOLAR;
  dscadsettings.polarity = BIPOLAR;
//  dscadsettings.gain = GAIN_2;
  dscadsettings.gain = GAIN_1;
  dscadsettings.load_cal = (BYTE)TRUE;
  dscadsettings.current_channel = 0;
  dscadsettings.scan_interval = 2; // allows the channel switching to be 10 mi  (original)
//  dscadsettings.scan_interval = 3; // allows the channel switching to be 5 mi

  // Apply A/D configurations
  if( ( result = dscADSetSettings( dscb, &dscadsettings ) ) != DE_NONE )
  {
          dscGetLastError(&errorParams);
          fprintf( stderr, "dscADSetSettings error: %s %s\n", 
                  dscGetErrorString(errorParams.ErrCode), 
                  errorParams.errstring );
          return 0;
  }
*/


  dscadscan.low_channel  = HK_CH_START; // First sequential HK channel 
  dscadscan.high_channel = HK_CH_END;   // Last  sequential HK channel
  dscadscan.gain = GAIN_1;

  // Allocate buffer space for incoming HK samples
  HKsamples = (DSCSAMPLE*)malloc( sizeof(DSCSAMPLE)
		 * ( dscadscan.high_channel - dscadscan.low_channel + 1 ) );
  // Set contents of HK accumulator array to zeros
  memset(HKaccum , 0 , sizeof(int) * ( HK_CH_END - HK_CH_START + 1 ) );


  for (i_sample_avg = 0 ; i_sample_avg < HK_NSAMPLES ; i_sample_avg++) 
  {
      // Scan the selected AD channels
      if( ( result = dscADScan( dscb, &dscadscan, HKsamples ) ) != DE_NONE ) 
      {  
              dscGetLastError(&errorParams);  
              fprintf( stderr, "dscADScan error: %s %s\n",   
                      dscGetErrorString(errorParams.ErrCode),   
                      errorParams.errstring );  
              free( HKsamples ); // remember to deallocate malloc() memory  
              return 0;  
      }  

      // Accumulate the integer A/D samples from multiple measurements
      // in the HKaccum array
      for( i = 0; i < (dscadscan.high_channel - dscadscan.low_channel)+ 1; i++) 
              HKaccum[i] = HKaccum[i] + (int) dscadscan.sample_values[i];
  }

  // Divide the accumulated samples by the number of samples
  // This averages the samples to reduce noise and only
  // has a 1-LSB rounding error (integer division always rounds down)
  for( i = 0; i < (dscadscan.high_channel - dscadscan.low_channel)+ 1; i++) 
        HKaccum[i] = HKaccum[i] / HK_NSAMPLES; //integer division


//



  // Print out HK readings converted to voltages
  //  if (config.verbose) {
//  if (preflightFlag) {
	  for( i = 0; i < (dscadscan.high_channel - dscadscan.low_channel)+ 1; i++)
	  {
                if( dscADCodeToVoltage(dscb, dscadsettings, HKaccum[i], &voltage) != DE_NONE)
                {
                        dscGetLastError(&errorParams);
                        fprintf( stderr, "dscADCodeToVoltage error: %s %s\n",
                                dscGetErrorString(errorParams.ErrCode), 
                                errorParams.errstring );
                        free( HKsamples ); // remember to deallocate malloc() memory
                        return 0;
                }
				
				HKvolts[i+1] = voltage; // insert into array of HK voltages
        }

		/////// Confirm value of shunt resistor on custom board (edit laser current calc) ///////
	  
            //For 2.6um Laser




	    HKvolts[8] = HKvolts[8] / 20.0; // laser current calculation (check R value on board)
            HKvolts[4] = pow(HKvolts[4],2.) * 137.68 - HKvolts[4] * 498.74 + 387.8; // Temp cal
            HKvolts[5] = pow(HKvolts[5],2.) * 137.68 - HKvolts[5] * 498.74 + 387.8 + 2.0;
            HKvolts[6] = pow(HKvolts[6],2.) * 137.68 - HKvolts[6] * 498.74 + 387.8; //

	    therr = (float)HKvolts[3];
	    therr = -56000.0*((float)therr/5.0)/(((float)therr/5.0)-1.0);
	    therr = (1.0/298.15) + (1.0/3810.0)*log((float)therr/30000.0);
	    HKvolts[3] = 1.0/(float)therr - 273.15;
//	    HKvolts[3] = pow(HKvolts[3],2.) * 137.68 - HKvolts[3] * 498.74 + 387.8;

            HKvolts[7] = HKvolts[7] * 290.22 - 3.3685; // pressure calibration 2012/04/12
	    HKvolts[12] = HKvolts[12] *2.0; // mass flow controller calibration
	    pres = HKvolts[7]; // save pressure in global variable for VMR estimation
            temp = (HKvolts[4]+HKvolts[6])/2;

if(preflightFlag) {

	    printf( "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n");
	    printf( " _________________________________________________________________________________\n");
            printf( " Output file basename :  %s\n",OutputFile); 
            printf( " Configuration file   :  %s\n",ConfigFile); 	  
	    printf( " _________________________________________________________________________________\n");
            printf( " Instrument readout:\n");
	    printf( " Laser current (A)    : %5.3f   |   Cell temp1 (degC)  : %5.3f\n",HKvolts[8],HKvolts[4] ) ;
	    printf( " Laser voltage (v)    : %5.3f   |   Cell temp2 (degC)  : %5.3f\n",HKvolts[9],HKvolts[6]);
	    printf( " Laser monitor (v)    : %5.3f   |   Base temp (degC)   : %5.3f\n",HKvolts[11],HKvolts[5]); 
            printf( " Laser temperature (v): %5.3f   |   Detector temp (v)  : %5.3f\n",HKvolts[3],HKvolts[2]);
            printf( " Mass flow rate(sLm)  : %5.3f   |   Cell press. (mb)   : %5.3f\n",HKvolts[12],HKvolts[7]);
            printf( " Absorption integral  : %5.3f   |                      : \n",VMRraw);
            printf( " _________________________________________________________________________________\n");
            printf( " 2.6um Laser Temp     : %5.3f   |   1.3um Laser Temp   : %5.3f\n",
               1.0/((1.0/298.15)+(1.0/3694.0)*log((10000.0*HKvolts[11]/(5.0-HKvolts[11]))/8606.0))-273.15,
               1.0/(0.001128+0.0002345*log(10000.0*HKvolts[11]/(5.0-HKvolts[11])) + 0.0000000873*pow(log(10000.0*HKvolts[11]/(5.0-HKvolts[11])),3.0))-273.15);

            printf( " _________________________________________________________________________________\n");
            printf( " Configuration readout:\n"); 
            printf( " vStart (v)           : %5.3f   |   Mass flow setpoint : %5.3f\n",config.vStart,config.MFC);
            printf( " vEnd (v)             : %5.3f   |   pp2f enable (1=Y)  : %5d\n",config.vEnd,config.pp2fEnable);
            printf( " vMod (v)             : %5.3f   |   Mins per file (m)  : %5d\n",config.vMod,config.minsPerFile);
            printf( " LSetPt (bits)        : %5.3f |   LSetPt (voltage)   : %5.3f\n",config.LSetPt,(config.LSetPt*1.1/1024));
            printf( " _________________________________________________________________________________\n");
  }

  // Write system time (secs and usec since UNIX epoch) to binary HK file
  gettimeofday(&tv, NULL);
  fwrite( &tv.tv_sec,  sizeof(int), 1 , ptr_HKfile); 
  fwrite( &tv.tv_usec, sizeof(int), 1 , ptr_HKfile); 
  // Write HouseKeeping values (as integers) to binary HK file
  fwrite( &HKaccum, sizeof(int), HKPTS, ptr_HKfile );

  free(HKsamples); // deallocate malloc() memory

  return 1; //Return success
}


int initHKfile() {

 char HKsuffix[10] = "_HK";
 char HKoutFilename[100]; 
 strcpy(HKoutFilename, OutputFile);
 strcat(HKoutFilename,HKsuffix);

 ptr_HKfile = fopen(HKoutFilename,"wb");
  if (!ptr_HKfile) {
        printf("Unable to open .HK (housekeeping) output file!");
        exit(EXIT_FAILURE);
  }

  // Insert ASCII portion on binary file format
  intBuff = HKPTS;
  fwrite( &intBuff, sizeof(int), 1, ptr_HKfile );  
  fwrite( &config.MFC, sizeof(float), 1, ptr_HKfile );
  fwrite( &config.vStart, sizeof(float), 1, ptr_HKfile );
  fwrite( &config.vEnd, sizeof(float), 1, ptr_HKfile );
  fwrite( &config.vMod, sizeof(float), 1, ptr_HKfile );
  fwrite( &config.pp2fEnable, sizeof(int), 1, ptr_HKfile );
  fwrite( &config.minsPerFile, sizeof(int), 1, ptr_HKfile );

  return 1;
}



int initSCfile() {

 char SCsuffix[10] = "_SC";
 char SCoutFilename[100]; 
 strcpy(SCoutFilename, OutputFile);
 strcat(SCoutFilename,SCsuffix);

 ptr_SCfile = fopen(SCoutFilename,"ab+");
  if (!ptr_SCfile) {
        printf("Unable to open .SC (scan) output file!");
        exit(EXIT_FAILURE);
  }

  // Insert ASCII header describing binary file format
  // 
  // [code here]

  // Insert config info and contents of config file
  intBuff = SCANPTS;
  fwrite( &intBuff, sizeof(int), 1, ptr_SCfile );
  intBuff = DARKINTERVAL;
  fwrite( &intBuff, sizeof(int), 1, ptr_SCfile );
  fwrite( &config.MFC, sizeof(float), 1, ptr_SCfile );
  fwrite( &config.vStart, sizeof(float), 1, ptr_SCfile );
  fwrite( &config.vEnd, sizeof(float), 1, ptr_SCfile );
  fwrite( &config.vMod, sizeof(float), 1, ptr_SCfile );
  fwrite( &config.pp2fEnable, sizeof(int), 1, ptr_SCfile );
  fwrite( &config.minsPerFile, sizeof(int), 1, ptr_SCfile );

  return 1;
}



int ACscan() {

  int pp2fRamps = 0; // index counter for ramp segments

  // Set all analog-to-digital configuration values to zero
  memset(&dscadsettings, 0, sizeof(DSCADSETTINGS));
  // Define new A/D configuration for scan operations
  dscadsettings.range = RANGE_10;
  dscadsettings.polarity = UNIPOLAR;
  dscadsettings.gain = GAIN_2;
  dscadsettings.load_cal = (BYTE)TRUE;
  dscadsettings.current_channel = 0;

  // Apply A/D configurations
  if( ( result = dscADSetSettings( dscb, &dscadsettings ) ) != DE_NONE )
  {
          dscGetLastError(&errorParams);
          fprintf( stderr, "dscADSetSettings error: %s %s\n", 
                  dscGetErrorString(errorParams.ErrCode), 
                  errorParams.errstring );
          return 0;
  }

  // Configure interrupt operation
  dscaioint.num_conversions	 = SCANPTS;
  dscaioint.conversion_rate	 = DA_OUTRATE;
  dscaioint.cycle 	  	 = (BYTE)FALSE;   
  dscaioint.internal_clock 	 = (BYTE)TRUE;
  dscaioint.low_channel		 = VINCH_DETECTD;
  dscaioint.high_channel	 = VINCH_DETECTD;
  dscaioint.external_gate_enable = (BYTE)FALSE;
  dscaioint.internal_clock_gate	 = (BYTE)FALSE; 
  dscaioint.fifo_enab 		 = (BYTE)TRUE;
  dscaioint.fifo_depth		 = SCANPTS;
  dscaioint.dump_threshold	 = SCANPTS;
  // Allocate buffer space for incoming scan samples
  dscaioint.sample_values = (DSCSAMPLE*)malloc( sizeof(DSCSAMPLE)
		 * dscaioint.num_conversions );

  // Write system time (UNIX epoch secs and usecs) to binary 
  //  PP2F file once / series of scan segments
  gettimeofday(&tv, NULL);
  fwrite( &tv.tv_sec,  sizeof(int), 1 , ptr_SCfile); 
  fwrite( &tv.tv_usec, sizeof(int), 1 , ptr_SCfile); 


  // Iterate through several scan sequences before pulling back to take housekeeping
  for ( i_sample_count = 0 ; i_sample_count < PP_PER_HK ; i_sample_count++ ) {

	  // Iterate through multiple segments of a pp2f ramp
	  for ( pp2fRamps = 0 ; pp2fRamps < PPRAMPSEGS ; pp2fRamps++ ) {

	              // Start A/D interrupt scans
                      dscs.transfers = 0;        
                      dscs.overflows = 0;        
                      dscs.op_type = OP_TYPE_INT;        

                      // Pause waveform generator
                      if( dscWGCommand(dscb, WG_CMD_PAUSE) != DE_NONE )  {
                             dscGetLastError(&errorParams);
                             fprintf( stderr, "dscWGCommandSet error: %s %s\n",
                                     dscGetErrorString(errorParams.ErrCode),
                                     errorParams.errstring );
                              free( dscaioint.sample_values ); // remember to deallocate malloc() memor
                             return 0;
                      }

                      // Reset waveform generator pointer to start of scan
                      if( dscWGCommand(dscb, WG_CMD_RESET) != DE_NONE )  {
                             dscGetLastError(&errorParams);
                             fprintf( stderr, "dscWGCommandSet error: %s %s\n",
                                     dscGetErrorString(errorParams.ErrCode),
                                     errorParams.errstring );
                              free( dscaioint.sample_values ); // remember to deallocate malloc() memor
                             return 0;
                      }

                     // Refill the waveform buffer with the next pp2f segment
                     for ( i = 0 ; i < SCANPTS ; i++ )
                      {
                             if( dscWGBufferSet(dscb, i, 
						ACscanRamp[i + (pp2fRamps * SCANPTS) ], VOUTCH_LASER, 1) != DE_NONE )
                             {
                                     dscGetLastError(&errorParams);
                                     fprintf( stderr, "dscWGBufferSet error: %s %s\n",
                                             dscGetErrorString(errorParams.ErrCode),
                                             errorParams.errstring );
                                     return 0;
                             }
                      }

                      // Initiate interrupt scans
                      if( ( result = dscADSampleInt( dscb, &dscaioint ) ) != DE_NONE )  {        
                              dscGetLastError(&errorParams);        
                              fprintf( stderr, "dscADSampleInt error: %s %s\n",        
                                      dscGetErrorString(errorParams.ErrCode),        
                                      errorParams.errstring );        
                              free( dscaioint.sample_values ); // remember to deallocate malloc() memor
                              return 0;        
                      }        

                      // Start waveform generator  
                      if( dscWGCommand(dscb, WG_CMD_START) != DE_NONE )  {
                             dscGetLastError(&errorParams);
                             fprintf( stderr, "dscWGCommandSet error: %s %s\n",
                                     dscGetErrorString(errorParams.ErrCode),
                                     errorParams.errstring );
                              free( dscaioint.sample_values ); // remember to deallocate malloc() memor
                             return 0;
                      }
                      
                      do{        
                              dscSleep(SLEEP_MS);        
                              dscGetStatus(dscb, &dscs);        
                      }while (dscs.op_type != OP_TYPE_NONE && !kbhit());        
                      
                  if ( dscs.overflows != 0 )
                              printf("WARNING!! Fifo Overflows: %lu", dscs.overflows );

                      // cancel interrupts manually for recycled mode or if interrupts are still runnin
                      if( dscs.op_type != OP_TYPE_NONE)        
                      {        
                              if( (result = dscCancelOp(dscb)) != DE_NONE)        
                              {        
                                      dscGetLastError(&errorParams);        
                                      fprintf( stderr, "dscCancelOp error: %s %s\n",        
                                              dscGetErrorString(errorParams.ErrCode),        
                                              errorParams.errstring );        
                                      free( dscaioint.sample_values ); // remember to deallocate malloc
                                      return 0;        
                              }        
                      }        
                    
                  if (config.verbose == 2) 
                  {
                            // Print incoming raw scan voltages
                            printf( "\nSample readouts:" );
                            for( i = 0; i < (dscaioint.num_conversions); i++)
                                    printf( " %hd", dscaioint.sample_values[i] );
                            printf( "\nActual voltages:" );
                            for( i = 0; i < (dscaioint.num_conversions); i++)
                            {
                                    if( dscADCodeToVoltage(dscb, dscadsettings, dscaioint.sample_values[i],  
                                            &voltage) != DE_NONE)
                                    {
                                            dscGetLastError(&errorParams);
                                            fprintf( stderr, "dscADCodeToVoltage error: %s %s\n", 
                                                    dscGetErrorString(errorParams.ErrCode), 
                                                    errorParams.errstring );
                                            free(dscaioint.sample_values);
                                            return 0;
                                    }
                                    printf( " %5.3lfV", voltage);
                            }
                            printf( "\n\n" );
                      } // End if verbose
            
              // Write pp2f scan values (as integers) to binary PP file
//              fwrite( &dscaioint.sample_values, sizeof(int), SCANPTS , ptr_SCfile );
//              printf("AC scan written to file.\n");
        } // End several-segment ramp series
  } // End several full scans # PP_PER_HK (# of full scans / HK write)

  free( dscaioint.sample_values ); // deallocate from malloc() call

  // Release driver resources
  // dscFree();

  return 1;

}


int DCscan() {

//if(TEMP_SCAN==1)
//{

double measurement=0.00;
double bitmeasurement=0.00;
int success=0;
float tempset=0.00;
int userchar='n';


/*
//Initialization for GnuPlot
char * commandsForGnuplot[] = {"set title \"TITLEEEE\"", "plot 'data.temp'"};
double xvals[NUM_POINTS] = {1.0, 2.0, 3.0, 4.0, 5.0};
double yvals[NUM_POINTS] = {5.0, 3.0, 1.0, 3.0, 5.0};
FILE * temp =  fopen("data.temp", "w");

FILE * gnuplotPipe = popen ("gnuplot", "w");

fprintf(gnuplotPipe, "plot '-' \n");
int indexy;
for (indexy = 0; indexy < NUM_POINTS; indexy++)
  {
   fprintf(gnuplotPipe, "%lff %lf\n", xvals[indexy], yvals[indexy]);
  }
fprintf(gnuplotPipe, "e");

for (indexy = 0; indexy < NUM_COMMANDS; indexy++)
  {
//   fprintf(gnuplotPipe, "%s \n", commandsForGnuplot(indexy]);
  }
getchar();
*/



//	DWORD currentcycle;
//	DWORD newcycle;
//	DWORD scansize;
//	scansize = SCANPTS;
	
	
DWORD last_total_transfers = 0;
DWORD last_transfers = 0;

int SCbuffer[(int)dscaioint.num_conversions];

int new_sample_count = 0;
int time_offset = 0;

double starttime, endtime;


memset(SCbuffer, 0 , sizeof(int)*dscaioint.num_conversions);

	startWGInterrupt();
//	dscGetStatus(dscb, &dscs);
//	currentcycle = (int)(dscs.total_transfers/scansize);

gettimeofday(&tv1, NULL);
starttime = (double)tv1.tv_sec*1000000.0f + (double)tv1.tv_usec*1.0f;

do{
   dscSleep(1);
   dscGetStatus(dscb, &dscs);
   new_sample_count = dscs.total_transfers - last_total_transfers;

   if(new_sample_count > dscaioint.num_conversions) {
      printf("Operation Failed: Not processing samples fast enough. %lu samples lost\n",new_sample_count - dscaioint.num_conversions);
      break;
   }

   if(dscs.transfers > last_transfers) {
      for( i = last_transfers; i < dscs.transfers && i < dscaioint.num_conversions; i++ ) {
         SCbuffer[i] = (int) dscaioint.sample_values[i]; 
      }
   } else if(dscs.transfers <= last_transfers) {
      for( i = last_transfers; i < dscaioint.num_conversions; i++ ) {
         SCbuffer[i] = (int) dscaioint.sample_values[i]; 
      }
   }

   if(dscs.transfers > dscaioint.fifo_depth) {
      last_transfers = dscs.transfers;
      last_total_transfers = dscs.total_transfers;
   }

   if(dscs.total_transfers >= dscaioint.num_conversions) {
      break;
   }
}while( dscs.op_type != OP_TYPE_NONE );

gettimeofday(&tv2, NULL);
endtime = (double)tv2.tv_sec*1000000.0f + (double)tv2.tv_usec*1.0f;

dscCancelOp(dscb);

float SCsample[SCANPTS];

  memset(SCsample, 0 , sizeof(float)*SCANPTS);
  for( i = 0; i < SCANPTS; i++) {
       if( dscADCodeToVoltage(dscb, dscadsettings, SCbuffer[i+SCANPTS], &voltage) != DE_NONE) {
		dscGetLastError(&errorParams);
      		fprintf( stderr, "dscADCodeToVoltage error: %s %s\n", 
			dscGetErrorString(errorParams.ErrCode), 
			errorParams.errstring );
      		free(dscaioint.sample_values);
      		return 0;
  	}
   SCsample[i] = voltage;
  }


  for ( i = 0 ; i < SCANPTS - 1; i++ ) {
    if((fabs(SCsample[i]) - fabs(SCsample[i+1]))>(float)0.1 && 
		fabs(SCsample[(int)((i+1)-(int)((i+1)/SCANPTS)*SCANPTS)]) < (float)0.1 && 
		fabs(SCsample[(int)((i+(int)(DARKINTERVAL/2)) - (int)((i+(int)(DARKINTERVAL/2))/SCANPTS)*SCANPTS)]) < (float)0.1 ) {
       time_offset = i - 1;
       break;
      }
  }
  if (time_offset  == -1)
	time_offset = SCANPTS-1;
  if (time_offset < 0 || time_offset>=SCANPTS)
     time_offset = 0;

double SCtimestep;
int SCsec = 0;
int SCusec = 0;

  for ( i_sample_count = 0 ; i_sample_count < (SC_PER_HK) ; i_sample_count++ ) {
        memset(SCaccum, 0 , sizeof(int)*SCANPTS);
        for (i_sample_avg = 0 ; i_sample_avg < SC_NSAMPLES ; i_sample_avg++)  {
            for(i = 0; i < SCANPTS; i++) {
                SCaccum[i] = SCaccum[i] + SCbuffer[time_offset + i + i_sample_avg*SCANPTS + i_sample_count*SCANPTS*SC_NSAMPLES];
            }
        }


SCtimestep = (double)(starttime+((double)(2*i_sample_count+1)*fabs(endtime-starttime)/(double)(2*SC_PER_HK)));
SCsec =	(int)floor(SCtimestep/1000000);
SCusec = (int)(SCtimestep-floor(SCtimestep/1000000)*1000000.0f);


        fwrite( &SCsec,  sizeof(int), 1 , ptr_SCfile); 
        fwrite( &SCusec, sizeof(int), 1 , ptr_SCfile); 

        // Write scan values (as integers) to binary SC file
        fwrite( &SCaccum, sizeof(int), SCANPTS , ptr_SCfile );
	//printf("DC scan written to file.\n")

  }
//printf("Elapsed Time: %f\n",endtime-starttime);
//getchar();

		if ( config.verbose == 2 ) {
                      // Print incoming raw scan voltages
                      printf( "\nSample readouts:" );
		      for ( i = 0; i < SCANPTS; i++)
			     printf( " %f",SCsample[i]);
                      printf( "\nActual voltages:" );
                      for( i = 0; i < SCANPTS; i++)
                      {
                              if( dscADCodeToVoltage(dscb, dscadsettings, SCaccum[i]/SC_NSAMPLES,  
                                      &voltage) != DE_NONE)
                              {
                                      dscGetLastError(&errorParams);
                                      fprintf( stderr, "dscADCodeToVoltage error: %s %s\n", 
                                              dscGetErrorString(errorParams.ErrCode), 
                                              errorParams.errstring );
                                      free(dscaioint.sample_values);
                                      return 0;
                              }
                              printf( " %5.3lfV", voltage);
                      }
                      printf( "\n\n" );
//getchar();
                } // End if verbose


/*
        // Write system time (secs and usec since UNIX epoch) to binary SC file
        gettimeofday(&tv, NULL);
        fwrite( &tv.tv_sec,  sizeof(int), 1 , ptr_SCfile); 
        fwrite( &tv.tv_usec, sizeof(int), 1 , ptr_SCfile); 

        // Write scan values (as integers) to binary SC file
        fwrite( &SCaccum, sizeof(int), SCANPTS , ptr_SCfile );
	//printf("DC scan written to file.\n");
  } // End for loop # DC scan writes / HK write
*/

  // Returns absolute height of absorption feature near line center
  // VMRraw = SCaccum[(SCANPTS-DARKINTERVAL)/2];

  // Returns integral over absorption feature, normalized by background intensity
  int startVal = (SCaccum[DARKINTERVAL+19]+SCaccum[DARKINTERVAL+20]+SCaccum[DARKINTERVAL+21])/3;
  int endVal   = (SCaccum[SCANPTS-19]+SCaccum[SCANPTS-20]+SCaccum[SCANPTS-21])/3;
  float stepSi = (endVal - startVal)/(SCANPTS-DARKINTERVAL-40);
  float integ = 0.0;
  for( i = DARKINTERVAL+20; i < SCANPTS-20 ; i++) 
  	integ = integ + (1.0 - SCaccum[i] / (startVal + stepSi*(i-DARKINTERVAL+20)));


  integ=integ/2;
  VMRraw = NAN;
  if(pres >= 10)
     VMRraw = (1091064.50914045*pow(pres,(-2.3456414321))*integ*integ+45144.6906365597*pow(pres,(-0.8843304381))*integ);
  rendpt = SCaccum[SCANPTS-1]*10.0/65535;


  free( dscaioint.sample_values ); // deallocate from malloc() call

  // Release driver resources
  // dscFree();

  return 1;
}


int setMFC(float MFCsetpoint) {
  int MFCsetDA;
  float DAscale;

  printf("Setting MFC to: %3.1f ... ",MFCsetpoint);
  // Write setpoint to MFC channel after conversion
  // from standard liters per minute (sLm) to AD range (2^16)
  DAscale = (float) DARANGE / DAVOLTS;
  MFCsetDA = (int)(DAscale * MFCSCALE * MFCsetpoint);

  // Write setpoint to DAC
  if( ( result = dscDAConvert( dscb, VOUTCH_MFC, MFCsetDA ) ) != DE_NONE )
    {
        dscGetLastError(&errorParams);
        fprintf( stderr, "dscDAConvert error: %s %s\n",
              dscGetErrorString(result), errorParams.errstring );
        return 0;
    }
  printf("Done. (D/A Code: %d)\n", MFCsetDA);

  return 1;
}

int setSetPt(float ArduinoSetPt) {

/*
int Output;
float DAscale;
if(ArduinoSetPt > (float)5.0){
ArduinoSetPt=(float)(5.0/1024.0*ArduinoSetPt); //Protection
}
DAscale = (float)(DARANGE/DAVOLTS);
Output = (int)(DAscale * ArduinoSetPt * 1.1/5.0);

if( ( result = dscDAConvert( dscb, VOUTCH_SETPT, Output) ) != DE_NONE )
  {
      dscGetLastError(&errorParams);
      fprintf(stderr, "dscDAConvert Error: %s %s\n",
            dscGetErrorString(result), errorParams.errstring );
      return 0;
  }
  printf("Done. (D/A Code: %d)\n", Output);
*/
  return 1;
}


void prepareToExit() {
        DSCDACODE dacode;
        DFLOAT zerovoltage;
        zerovoltage = 0.0;
        
	printf("\n");
	result = setMFC( 0.0 );
	result = dscWGCommand(dscb, WG_CMD_PAUSE);
        result = dscVoltageToDACode( dscb, dscdasettings, zerovoltage, &dacode);
        result = dscDAConvert( dscb, VOUTCH_LASER, dacode);
	result = dscFreeBoard(dscb);
	result = dscFree();
	fclose(ptr_HKfile);
	fclose(ptr_SCfile);
	printf("Shutdown complete. \n");
}

int autoCal() {
  ////////////// Perform Autocalibration ///////////////
  DSCADCALPARAMS dscadcalparams;
  
  dscadcalparams.adrange = 255;		// calibrate all A/D modes
  dscadcalparams.boot_adrange = 8;	// set power-up A/D mode to +/-10V
  
  if ((result = dscADAutoCal(dscb, &dscadcalparams)) != DE_NONE)
  {
    dscGetLastError(&errorParams);
    fprintf(stderr, "dscADAutoCal failed: %s (%s)\n",
    dscGetErrorString(result), errorParams.errstring);
    return 0;
  }

  return 1;
}

int DMMinit() {
  // Initialize all elements of board setting structure to zero.
  memset(&dsccb, 0, sizeof(DSCCB));
  dsccb.boardtype = DSC_DMM32DX;
  dsccb.base_address = 0x300;   
  dsccb.int_level = 7; // interrupt level
  // This line seems to cause the DAC to not work.
    dsccb.DAC_Config = 1; // for 16-bit DAC usage

 // Initialize Universal Driver software
   if ((result = dscInit(DSC_VERSION)) != DE_NONE)
   {
         dscGetLastError(&errorParams);
         fprintf(stderr, "dscInit failed: %s (%s)\n",
             dscGetErrorString(result), errorParams.errstring);
         return 0;
    }

  // Initialize Diamond DMM-32DX-AT I/O board
  if ((result = dscInitBoard(DSC_DMM32DX, &dsccb, &dscb)) != DE_NONE)
    {
      dscGetLastError(&errorParams);
      fprintf(stderr, "dscInitBoard failed: %s (%s)\n",
              dscGetErrorString(result), errorParams.errstring);
      return 0;
    }

  dscdasettings.polarity = UNIPOLAR;
  dscdasettings.load_cal = TRUE;
  dscdasettings.range    = 5.0;


  dscadsettings.range = RANGE_5;
  dscadsettings.polarity = BIPOLAR;
  dscadsettings.gain = GAIN_1;
  dscadsettings.load_cal = (BYTE)TRUE;
  dscadsettings.current_channel = 0;
  dscadsettings.scan_interval = 2;

  // Enable enhanced features on DMM board (is this necessary?)
  if((result = dscEnhancedFeaturesEnable( dscb, (BOOL)TRUE )) != DE_NONE )
    {
      dscGetLastError(&errorParams);
      fprintf( stderr, "dscEnhancedFeaturesEnable error: %s %s\n",
          dscGetErrorString(result), errorParams.errstring);
      return 0;
    }

  printf("Running DMM I/O autocalibration (15 secs)...\n");
  if( (result = autoCal()) == 0 )
  {
    fprintf( stderr, "dsc Auto Calibration error.");
    return 0;
  }  

  if( ( result = dscADSetSettings( dscb, &dscadsettings ) ) != DE_NONE ) {
    dscGetLastError(&errorParams);
    fprintf(stderr, "dscADSetSettings error: %s %s\n",
	dscGetErrorString(errorParams.ErrCode),
	errorParams.errstring);
    return 0;
  }

  if( ( result = dscDASetSettings( dscb, &dscdasettings ) ) != DE_NONE ) {
    dscGetLastError(&errorParams);
    fprintf(stderr, "dscDASetSettings error: %s %s\n",
	dscGetErrorString(errorParams.ErrCode),
	errorParams.errstring);
    return 0;
  }


  ////////////// Setup waveform generator //////////////

  createDCScanRamp();
  // Build configuration structure from values in header
  dscWGconfig.depth = (DWORD)SCANPTS; // # pts in scan (AC will be multiple of this)
  dscWGconfig.ch_per_frame = (DWORD)(DA_CH_PER_FRAME - 1); // # pts to output each clock
  dscWGconfig.source = (DWORD)DA_CLK_SOURCE; // clock input source; 1=ctr0,2=ctr1&2

  // Set both counter rates to ensure consistency if counter selection changes
  dscCounterSetRateSingle(dscb, (float)DA_OUTRATE, COUNTER_1_2);
  dscCounterSetRateSingle(dscb, (float)DA_OUTRATE, COUNTER_0);

  // Reset the pointer to the D/A buffer
  if( dscWGCommand(dscb, WG_CMD_RESET) != DE_NONE ) 
  {
          dscGetLastError(&errorParams);
          fprintf( stderr, "dscWGCommand error: %s %s\n", 
                  dscGetErrorString(result), 
                  errorParams.errstring );
          return 0;
  }
  // Initialize the configuration
  if( dscWGConfigSet(dscb, &dscWGconfig) != DE_NONE ) 
  {
          dscGetLastError(&errorParams);
          fprintf( stderr, "dscWGConfigSet error: %s %s\n", 
                  dscGetErrorString(result),
                  errorParams.errstring );
          return 0;
  }
  
  int i;
  for( i=0; i<SCANPTS; i++) {
    if( dscWGBufferSet(dscb, i, DCscanRamp[i], VOUTCH_LASER, 1) != DE_NONE ) {
      dscGetLastError(&errorParams);
      fprintf( stderr, "dscWGBufferSet error: %s %s\n",
		dscGetErrorString(result),
		errorParams.errstring );
      return 0;
      }
  } 


  //dscCounterDirectSet(dscb,&dsccr);

//  WGStartTime = clock();
    dscGetStatus(dscb, &dscs);

		// Configure interrupt operation
		dscaioint.num_conversions	 = (int)SCANPTS*(SC_NSAMPLES*SC_PER_HK+1);
		dscaioint.conversion_rate	 = DA_OUTRATE;
		dscaioint.cycle 	  	 = (BYTE)TRUE;   
		dscaioint.internal_clock  	 = (BYTE)TRUE;   
		dscaioint.low_channel		 = VINCH_DETECTD;
		dscaioint.high_channel		 = VINCH_SENSED;
		dscaioint.external_gate_enable   = (BYTE)FALSE;
		dscaioint.internal_clock_gate   = (BYTE)FALSE;
		dscaioint.fifo_enab 		 = (BYTE)TRUE;
		dscaioint.fifo_depth 		 = (int)(SCANPTS/4);
		dscaioint.dump_threshold	 = (int)(SCANPTS/4);
		dscaioint.sample_values = (DSCSAMPLE*)malloc( sizeof(DSCSAMPLE)
			* dscaioint.num_conversions );


  clock_gettime(CLOCK_MONOTONIC, &WGStartTime);

		if( ( result = dscADScanInt( dscb, &dscaioint ) ) != DE_NONE )  {        
			dscGetLastError(&errorParams);        
			fprintf( stderr, "dscADSampleInt error: %s %s\n",        
				dscGetErrorString(errorParams.ErrCode),        
				errorParams.errstring );        
			free( dscaioint.sample_values ); // remember to deallocate malloc() memor
//			return 0;        
		}        



//  clock_gettime(&WGStartTime, NULL);
  dscWGCommand(dscb, WG_CMD_START);

//getchar();

  dscCancelOp(dscb);

//  dscuserintfunction.int_mode = USER_INT_AFTER;
//  dscuserintfunction.int_type = INT_TYPE_DA;
//  dscSetUserInterruptFunction(dscb,&dscuserintfunction);

//   memset(&dsccr, 0, sizeof(DSCCR));
//   dsccr.control_code = (BYTE)216;

//   dsccr.control_code = (BYTE)0b11001110;
//   dsccr.counter_number = (BYTE)2;
//   dsccr.counter_data = (DWORD)65535;
//  int oldval;

//  DWORD time_now;
int iterate = 0;
//  do {
//    WGCurrentTime = clock();

//    clock_gettime(CLOCK_MONOTONIC, &WGCurrentTime);

//    dscGetTime(&time_now);
//    printf("Time Now: %f   :   Time/1000: %f\n",time_now*1.0,time_now/1000);

//    dscCounterRead(dscb,&dsccr);
//    printf("Counter Value 1:  %lu  |   Counter Value 2:  %lu  |  Counter Value 3:  %lu  |  Counter Divisor:  %lu\n",dsccr.counter0.value,dsccr.counter1.value,dsccr.counter2.value,dsccr.counter_data);

//    printf("First Attempt: %lu     |     Second Attempt: %lu\n", (dsccr.counter1.value<<8)|dsccr.counter2.value,(dsccr.counter2.value<<8)|dsccr.counter1.value);

//    printf("Counter Divisor Value: %u\n",dsccr.counter_data);

//    printf("Time Elapsed: %f   |    Finer Resolution: %llu\n", 
//	(double)(WGCurrentTime - WGStartTime)/CLOCKS_PER_SEC*1000,
//	(long long unsigned int)(1000*1000*1000*(tv2.tv_sec - tv1.tv_sec)+(tv2.tv_nsec - tv1.tv_nsec)));

//    WGelapsed = 1000000000.0*(WGCurrentTime.tv_sec - WGStartTime.tv_sec) + (WGCurrentTime.tv_nsec - WGStartTime.tv_nsec);
//    WGindex =  (WGelapsed*DA_OUTRATE/1000000000) - floor((WGelapsed*DA_OUTRATE/1000000000)/1024)*1024;
//    printf("Finer Resolution: %f    |    Position in Waveform Generator: %u\n",WGelapsed,WGindex);

//    iterate++;
//    if( iterate == 1000 ) {
//	iterate = 0;//
//	getchar();
//   }
//  }while(1==1);


//dscGetStatus(dscb,&dscs);

//printf("Waveform has started?");
//getchar();
	return 1;
}


int checkConfig() {

  if (config.MFC < MINMFC){
    printf("config.txt error: MFC < %f. Was %f, setting to %f.\n",MINMFC,config.MFC,MINMFC);
    config.MFC = MINMFC;
  }
  if (config.MFC > MAXMFC){
    printf("config.txt error: MFC > %f. Was %f, setting to %f.\n",MAXMFC,config.MFC,MAXMFC);
    config.MFC = MAXMFC;
  }
  if (config.vStart < MINVSTART){
    printf("config.txt error: vStart < %f. Was %f, setting to %f.\n",MINVSTART,config.vStart,MINVSTART);
    config.vStart = MINVSTART;
  }
  if (config.vStart > MAXVSTART){
    printf("config.txt error: vStart > %f. Was %f, setting to %f.\n",MAXVSTART,config.vStart,MAXVSTART);
    config.vStart = MAXVSTART;
  }
  if (config.vEnd < MINVEND){
    printf("config.txt error: vEnd < %f. Was %f, setting to %f.\n",MINVEND,config.vEnd,MINVEND);
    config.vEnd = MINVEND;
  }
  if (config.vEnd > MAXVEND){
    printf("config.txt error: vEnd > %f. Was %f, setting to %f.\n",MAXVEND,config.vEnd,MAXVEND);
    config.vEnd = MAXVEND;
  }
  if (config.vMod < MINVMOD){
    printf("config.txt error: vMod < %f. Was %f, setting to %f.\n",MINVMOD,config.vMod,MINVMOD);
    config.vMod = MINVMOD;
  }
  if (config.vMod > MAXVMOD){
    printf("config.txt error: vMod > %f. Was %f, setting to %f.\n",MAXVMOD,config.vMod,MAXVMOD);
    config.vMod = MAXVMOD;
  }
  if ((config.pp2fEnable != 0 && config.pp2fEnable != 1)) { // if pp2fEnable is set to other than 0 or 1:
    printf("config.txt error: pp2fEnable must equal 0 or 1. Was %d, setting to %d.\n",
	   config.pp2fEnable,PP2FDEFAULT);
    config.pp2fEnable = PP2FDEFAULT;
  }
  if (config.minsPerFile < MINMINSPERFILE) {
    printf("config.txt error: minsPerFile < %d. Was %d, setting to %d.\n",
	   MINMINSPERFILE,config.minsPerFile,MINMINSPERFILE);
    config.minsPerFile = MINMINSPERFILE;
  }
  if (config.minsPerFile > MAXMINSPERFILE) {
      printf("config.txt error: minsPerFile > %d. Was %d, setting to %d.\n",
	     MAXMINSPERFILE,config.minsPerFile,MAXMINSPERFILE);
      config.minsPerFile = MAXMINSPERFILE;
  }
  if (config.vEnd < config.vStart) {
    printf("config.txt error: vEnd (%f) < vStart (%f). Setting vEnd = vStart.\n",config.vEnd,config.vStart);
    config.vEnd = config.vStart;
  }
  if ((config.vEnd + config.vMod) > LASERVMAX) {
    printf("config.txt error: The total laser voltage may exceed safe limits!!\n");
    printf("Check the parameter file (config.txt) for appropriate vEnd and vMod values.\n");
    printf("Exiting noW!\n");
    exit(EXIT_FAILURE);
  }
  if ((config.verbose != 0) && (config.verbose != 1) && (config.verbose != 2)) {
    printf("config.txt error: The verbose setting must be integer = 0,1, or 2.\n");
    printf("Verbose output turned off (=0).\n");
    config.verbose = 0;
  } 
  if ((config.sendUDP != 0) && (config.sendUDP != 1)) {
    printf("config.txt error: The sendUDP setting must be integer = 0 or 1.\n");
    printf("UDP transmissions turned off (=0).\n");
    config.verbose = 0;
  } 
  return 1;
}


void createACScanRamp() {
  int iramp; // index counter over ramp points
  float ADscale; // voltage to DA count conversion
  float step; // voltage interval between points
  float modul[PPSCANPTS]; // array of 1-f modulation
   
  // Determine size of voltage step between scan points
  step = (config.vEnd - config.vStart) / ( PPSCANPTS - DARKINTERVAL );
  
  // Determine range conversion factor from voltage to DA count
  ADscale = (float)(DARANGE) / DAVOLTS;

  // Set first values in scan to zero to create a period
  // for  dark count with length DARK_INTERVAL 
  for (iramp = 0 ; iramp < DARKINTERVAL ; iramp++)
    ACscanRamp[iramp] = (int) 0;

  // Set rest of scan ramp to a linear trend between vStart and vEnd
  // plus a 1-f modulation
  for ( iramp = DARKINTERVAL ; iramp < PPSCANPTS ; iramp++ ) 
  {
  	modul[iramp] = config.vMod * 
    		sinf( ( (float) iramp / (float) PPWAVEPTS ) * (float) 2.0 * PI );
  	ACscanRamp[iramp] = (int)( ADscale * 
		(config.vStart + step * (iramp - DARKINTERVAL ) + modul[iramp] ) );       
  }

//  for ( iramp = 0 ; iramp < PPSCANPTS ; iramp++ ) 
//	  printf("%d ",ACscanRamp[iramp]);

  printf("\n");

}


void createDCScanRamp() {
  int iramp;
  float step,ADscale;
  float modamp = 0.2;
   
  // Determine size of voltage step between scan points
  step = (config.vEnd - config.vStart) / ( SCANPTS - DARKINTERVAL );

  // Determine range conversion factor from voltage to DA count
  ADscale = (float)(DARANGE) / DAVOLTS;

  // Set first values in scan to zero to create a period
  // for  dark count with length DARK_INTERVAL 

  if ( USE_PP2F == 0 )
    {
     for (iramp = 0 ; iramp < DARKINTERVAL ; iramp++)
        DCscanRamp[iramp] = 0;

     // Set rest of scan ramp to a linear trend between vStart and vEnd
     for (iramp = DARKINTERVAL ; iramp < SCANPTS ; iramp++)
        DCscanRamp[iramp] = (int)((config.vStart + step * (iramp - DARKINTERVAL )) * ADscale);

     return;
    }

  if(4.0*modamp > (config.vEnd - config.vStart))
     modamp = (config.vEnd - config.vStart)/4.0;
    

  step = (config.vEnd - config.vStart - 2.0*modamp) / ( SCANPTS - DARKINTERVAL );
  for (iramp = 0; iramp < DARKINTERVAL ; iramp++)
     DCscanRamp[iramp] = 0;
  
  for (iramp = DARKINTERVAL; iramp < SCANPTS ; iramp++)
    {
      DCscanRamp[iramp] = (int)((config.vStart + modamp + modamp*sin(iramp*PI*2.0*(1.0/32.0)) + step*(iramp)) * ADscale);
    }



//      DCscanRamp[iramp] = (int)((config.vEnd + 0 * (iramp - DARKINTERVAL )) * ADscale);

  // Print scan ramp to screen for diagnostics
  //for (iramp = 0 ; iramp < SCANPTS ; iramp++)
  //   printf(" %d", scanRamp[iramp]);
}

void startWGInterrupt() {

/*
		dscadsettings.range = RANGE_5;
		dscadsettings.polarity = BIPOLAR;
		dscadsettings.gain = GAIN_1;
		dscadsettings.load_cal = (BYTE)TRUE;
		dscadsettings.current_channel = 0;

		if( ( result = dscADSetSettings( dscb, &dscadsettings ) ) != DE_NONE ) {
			dscGetLastError(&errorParams);
			fprintf( stderr, "dscADSetSettings error: %s %s\n", 
                dscGetErrorString(errorParams.ErrCode), 
                errorParams.errstring );
		}
*/
	
    dscGetStatus(dscb, &dscs);
	//dscs.transfers = 0;        
    //dscs.overflows = 0;        
    //dscs.op_type = OP_TYPE_INT; 

    if ( dscs.op_type == OP_TYPE_NONE || dscs.overflows > 0 ) {  

//printf("Starting Waveform Generator. Press any key to continue");
//getchar();

		if ( dscs.overflows != 0 ) {
			printf("WARNING!! Fifo Overflows: %lu", dscs.overflows );
			// cancel interrupts manually for recycled mode or if interrupts are still runnin
			if( dscs.op_type != OP_TYPE_NONE) {
				if( (result = dscCancelOp(dscb)) != DE_NONE)        
				{        
					dscGetLastError(&errorParams);        
					fprintf( stderr, "dscCancelOp error: %s %s\n",        
						dscGetErrorString(errorParams.ErrCode),        
						errorParams.errstring );        
					free( dscaioint.sample_values ); // remember to deallocate malloc
//					return 0;        
				}        
			}    
		}
/*
		for (i=0; i<SCANPTS; i++) {
			if( dscWGBufferSet(dscb, i, DCscanRamp[i], VOUTCH_LASER, 1) != DE_NONE ) {
				dscGetLastError(&errorParams);
				fprintf( stderr, "dscWGBufferSet error: %s %s\n",
					dscGetErrorString(errorParams.ErrCode),
					errorParams.errstring );
//				return 0;
			}
		}
*/

/*
		// Set all analog-to-digital configuration values to zero
		memset(&dscadsettings, 0, sizeof(DSCADSETTINGS));
		// Define new A/D configuration for scan operations 
		dscadsettings.range = RANGE_5;
		dscadsettings.polarity = BIPOLAR;
		dscadsettings.gain = GAIN_1;
		dscadsettings.load_cal = (BYTE)TRUE;
		dscadsettings.current_channel = 0;
		dscadsettings.scan_interval = 3;

		// Apply A/D configurations
		if( ( result = dscADSetSettings( dscb, &dscadsettings ) ) != DE_NONE ) {
			dscGetLastError(&errorParams);
			fprintf( stderr, "dscADSetSettings error: %s %s\n", 
                dscGetErrorString(errorParams.ErrCode), 
                errorParams.errstring );
//			return 0;
		}
*/


		// Configure interrupt operation
		dscaioint.num_conversions	 = (int)SCANPTS*(SC_NSAMPLES*SC_PER_HK+1);
		dscaioint.conversion_rate	 = DA_OUTRATE;
		dscaioint.cycle 	  	 = (BYTE)TRUE;   
		dscaioint.internal_clock 	 = (BYTE)TRUE;
		dscaioint.low_channel		 = VINCH_DETECTD;
		dscaioint.high_channel	 	 = VINCH_DETECTD;
		dscaioint.external_gate_enable   = (BYTE)FALSE;
		dscaioint.internal_clock_gate	 = (BYTE)FALSE; 
		dscaioint.fifo_enab 		 = (BYTE)TRUE;
//		dscaioint.fifo_depth		 = SCANPTS;
		dscaioint.fifo_depth		 = (int)(SCANPTS/4);
//		dscaioint.dump_threshold	 = SCANPTS;
		dscaioint.dump_threshold	 = (int)(SCANPTS/4);
		// Allocate buffer space for incoming scan samples
		dscaioint.sample_values = (DSCSAMPLE*)malloc( sizeof(DSCSAMPLE)
			* dscaioint.num_conversions );

		 
/*		 
		if( dscWGCommand(dscb, WG_CMD_PAUSE) != DE_NONE )  {
			dscGetLastError(&errorParams);
			fprintf( stderr, "dscWGCommandSet error: %s %s\n",
				dscGetErrorString(errorParams.ErrCode),
				errorParams.errstring );
			free( dscaioint.sample_values ); // remember to deallocate malloc() memor
//			return 0;
		}


		// Reset waveform generator pointer to start of scan
		if( dscWGCommand(dscb, WG_CMD_RESET) != DE_NONE )  {
			dscGetLastError(&errorParams);
			fprintf( stderr, "dscWGCommandSet error: %s %s\n",
				dscGetErrorString(errorParams.ErrCode),
				errorParams.errstring );
			free( dscaioint.sample_values ); // remember to deallocate malloc() memor
//			return 0;
		}
                
		dscSleep(2);
  */            
//dscSleep(5);

//   clock_gettime(CLOCK_MONOTONIC, &WGCurrentTime);
//   WGelapsed = 1000000000.0*(WGCurrentTime.tv_sec - WGStartTime.tv_sec) + (WGCurrentTime.tv_nsec - WGStartTime.tv_nsec);
//int  oldWGindex =  (WGelapsed*DA_OUTRATE/1000000000) - floor((WGelapsed*DA_OUTRATE/1000000000)/1024)*1024;

//int howmany = 0;

/*
do
  {
   clock_gettime(CLOCK_MONOTONIC, &WGCurrentTime);
   WGelapsed = 1000000000.0*(WGCurrentTime.tv_sec - WGStartTime.tv_sec) + (WGCurrentTime.tv_nsec - WGStartTime.tv_nsec);
   WGindex =  (WGelapsed*DA_OUTRATE/1000000000) - floor((WGelapsed*DA_OUTRATE/1000000000)/1024)*1024;
//printf("WG Index:  %u" , WGindex);
   if(WGindex == 0) {
     break;
   }
//  howmany++;
  }while(1==1);
//printf("How Many iterations: %u    |   How long it took: %f\n", howmany, WGelapsed);
//getchar();
*/



		// Initiate interrupt scans
		if( ( result = dscADScanInt( dscb, &dscaioint ) ) != DE_NONE )  {        
			dscGetLastError(&errorParams);        
			fprintf( stderr, "dscADSampleInt error: %s %s\n",        
				dscGetErrorString(errorParams.ErrCode),        
				errorParams.errstring );        
			free( dscaioint.sample_values ); // remember to deallocate malloc() memor
//			return 0;        
		}        

/*
		// Start waveform generator  
		if( dscWGCommand(dscb, WG_CMD_START) != DE_NONE )  {
//		if( dscWGCommand(dscb, WG_CMD_RESET) != DE_NONE )  {
			dscGetLastError(&errorParams);
			fprintf( stderr, "dscWGCommandSet error: %s %s\n",
				dscGetErrorString(errorParams.ErrCode),
				errorParams.errstring );
				free( dscaioint.sample_values ); // remember to deallocate malloc() memor
//			return 0;
		}	
*/
	 //dscSleep(2);
	}
}


int getOutputFilename() {
  FILE *refFile;
  int  suffixNum = 1; // Suffix numeral
  char suffixNumChar[10]; // Suffix numeral as formatted text
  char OutputFileOriginal[100]; // holds original output filename

  // Define output filename structure, with time code format info
  //  const char fmt[] = "CLH2-%Y%m%d_%H%M_%j_%z-CLH2_Outfile";  //older version with time zone and DOY
  const char fmt[] = "/home/dscguest/clh2ops/data/CLH2-%Y%m%d_%H%M";  
  size_t n = sizeof ( fmt );

  time_t init = time ( NULL );
  // Populate filename format string with local time info
  // The value n+6 accounts for expansion of 2-char format codes
  // into longer sequences when populated (%Y -> 1969)
  strftime (OutputFile,n+6,fmt, gmtime ( &init ) );

  char HKsuffix[8] = "_HK";			
  char SCsuffix[8] = "_SC";

  // Additional suffix if operating in preflight mode.
  //if ( preflightFlag == 1 ) 
  //{
  //         char PREsuffix[10] = "_preFlight";
  //	   strcat(OutputFile, PREsuffix);
  //}

  // Assemble filenames
   char HKoutFilename[CHARLENGTH]; 
   strcpy(HKoutFilename, OutputFile);
   strcat(HKoutFilename,HKsuffix);
   char SCoutFilename[CHARLENGTH]; 
   strcpy(SCoutFilename, OutputFile);
   strcat(SCoutFilename,SCsuffix);

   ////// Check if file with this name already exists: //////

   // Save original output filename
   strcpy(OutputFileOriginal, OutputFile);

  struct stat buffer;
  while ( stat (HKoutFilename, &buffer) ==0 || stat (SCoutFilename, &buffer) ==0  )	
  {
     sprintf(suffixNumChar,"_%02d",suffixNum); // create '_##' string

     memset(OutputFile, 0, CHARLENGTH);	// Erase char array     
     strcpy(OutputFile, OutputFileOriginal); // Fill with base filename (no suffix)
     strcat(OutputFile, suffixNumChar); // Append suffix

     // Create _HK and _SC filenames 
     strcpy(HKoutFilename, OutputFile);
     strcat(HKoutFilename, HKsuffix);
     strcpy(SCoutFilename, OutputFile);
     strcat(SCoutFilename, SCsuffix);
	
     printf("WARNING: File exists!!! Check system time and computer clock battery.\n");
     
     suffixNum++; // Increment suffix number
   }

  printf("File basename is: %s \n", OutputFile );

  // To support an auxiliary program to read the most current output
  // data, we create a basic file containing the ASCII base filename
  // of the current output files ('OutputFile')
  refFile = fopen(activeFileRef,"w");
  fprintf(refFile,"%s\n", HKoutFilename);
  fprintf(refFile,"%s", SCoutFilename);
  fclose(refFile);

  // Set file start time, so we can know when to start next file (chunking)
  fileStart_secondsUNIX = time( NULL ); 
  
  return 1;
}


int readConfig() {
 FILE *parfile;
 char *mode = "r";
 char parbuff[1024];
 float MFC;

 // Write null values to contents of buffer
 memset(parbuff,'\0',sizeof(parbuff));
 parfile = fopen(ConfigFile,mode);

 // If file can not be opened 
if (parfile == NULL) {
   printf("Can't open parameter file: %s\nParameter file must reside in the local folder.",ConfigFile);
   exit(EXIT_FAILURE);
 }
 else
 {
   printf("Loaded parameter file: %s\n",ConfigFile);
 }

 // Parse each line and save to config structure 
 fgets(parbuff,sizeof(parbuff),parfile);
 sscanf(parbuff,"%f ",&config.MFC);
 memset(parbuff,'\0',sizeof(parbuff));
 fgets(parbuff,sizeof(parbuff),parfile);
 sscanf(parbuff,"%f ",&config.vStart);
 memset(parbuff,'\0',sizeof(parbuff));
 fgets(parbuff,sizeof(parbuff),parfile);
 sscanf(parbuff,"%f ",&config.vEnd);
 memset(parbuff,'\0',sizeof(parbuff));
 fgets(parbuff,sizeof(parbuff),parfile);
 sscanf(parbuff,"%f ",&config.vMod);
 memset(parbuff,'\0',sizeof(parbuff));
 fgets(parbuff,sizeof(parbuff),parfile);//Modified section for Arduino set pt
 sscanf(parbuff,"%f",&config.LSetPt); //Modified section for Arduino set pt
 memset(parbuff,'\0',sizeof(parbuff)); //Modified section for Arduino set pt
 fgets(parbuff,sizeof(parbuff),parfile);
 sscanf(parbuff,"%d ",&config.pp2fEnable);
 memset(parbuff,'\0',sizeof(parbuff));
 fgets(parbuff,sizeof(parbuff),parfile);
 sscanf(parbuff,"%d ",&config.minsPerFile);
 memset(parbuff,'\0',sizeof(parbuff));
fgets(parbuff,sizeof(parbuff),parfile);
 sscanf(parbuff,"%d ",&config.verbose);
 memset(parbuff,'\0',sizeof(parbuff));
fgets(parbuff,sizeof(parbuff),parfile);
 sscanf(parbuff,"%d ",&config.sendUDP);
 memset(parbuff,'\0',sizeof(parbuff));

 fclose(parfile);

 // Verify that all parameters are within ranges defined in header
 checkConfig();
 return 1;
}


void handleInterrupt( int sig ) {
      printf("Interrupted...\n");
      prepareToExit();
      exit(sig);
}


int main(int argc, char *argv[]) {
      
      char key=0;
      int ch;
      int statusCt=0;
      int ret;

      // If C-c interrupt is received, try to run exit script
      signal(SIGINT, handleInterrupt);


      // Output time stamp into logfile to note that function has started
      FILE *refFile;  
      const char fmt[] = "Operating code 'main' initiated at: %Y/%m/%d %H:%M:%S";
      size_t n = sizeof ( fmt );
      time_t init = time ( NULL );
      // Populate filename format string with local time info
      // The value n+6 accounts for expansion of 2-char format codes
      // into longer sequences when populated (%Y -> 1969)
      strftime (timestamp,n+6,fmt, gmtime ( &init ) );
      // Write to log file
      refFile = fopen(StartLogFile,"a"); // append date string to file
      fprintf(refFile,"%s\n", timestamp);
      fclose(refFile);
                                                                              

      // Read command line options to look for preflight flag:
      // main -p
      while ((ch = getopt(argc, argv, "p")) != -1)
      {
              switch (ch) 
              { 
              case 'p':  // Flag present, set to 1. 
                      preflightFlag = 1; 
                      printf(" \n *************************************\n");
                      printf(" *** Operating in pre-flight mode. ***\n");
                      printf(" *************************************\n\n");
                      break; 
              default: /* If unknown options present, print error message. */
                      (void)fprintf(stderr, "Usage: %s [-p]\n", argv[0]); 
                      exit(EXIT_FAILURE);
              } 
      } 
	  
      // Read in configuration file
      if ( readConfig() != 1) {
            printf("readConfig failed.");
            exit(EXIT_FAILURE);
      }
      // Build output file base name from system time; check for name conflict
      if ( getOutputFilename() != 1) {
            printf("getOutputFilename failed.");
            exit(EXIT_FAILURE);
      }
      // Open HK (housekeeping) output file; write headers
      if ( ( initHKfile() != 1 ) ) {
            printf("initHKfile failed.");
            exit(EXIT_FAILURE);
	  }

      // Open SC (scan) output file; write headers
      if ( ( initSCfile() != 1 ) ) {
            printf("initSCfile failed.");
            exit(EXIT_FAILURE);
      }

        // Setup UDP broadcast output  
        int sock;                         /* Socket */
        struct sockaddr_in broadcastAddr; /* Broadcast address */
//        char sendString[100];                 /* String to broadcast */
//        char UDPtime[20];
        char sendString[2000];
        int broadcastPermission;          /* Socket opt to set permission to broadcast */
        unsigned int sendStringLen;       /* Length of string to broadcast */
//        char *broadcastIP = "192.168.84.1"; /* broadcast IP address */
//        unsigned short broadcastPort = 41006;    /* broadcast port */

        char *broadcastIP = "192.168.184.1";

//        char *broadcastIP = "192.168.184.1";
        unsigned short broadcastPort = 30129;
        
        /* Create socket for sending/receiving datagrams */
        if ((sock = socket(PF_INET, SOCK_DGRAM, IPPROTO_UDP)) < 0)
        {
            printf("socket() failed");
            exit(EXIT_FAILURE);
        }   

        /* Set socket to allow broadcast */
        broadcastPermission = 1;
        if (setsockopt(sock, SOL_SOCKET, SO_BROADCAST, (void *) &broadcastPermission,
              sizeof(broadcastPermission)) < 0)
        {
            printf("setsockopt() failed");
            exit(EXIT_FAILURE);
        }
        /* Construct local address structure */
        memset(&broadcastAddr, 0, sizeof(broadcastAddr));   /* Zero out structure */
        broadcastAddr.sin_family = AF_INET;                 /* Internet address family */ 
        broadcastAddr.sin_addr.s_addr = inet_addr(broadcastIP);/* Broadcast IP address */ 
        broadcastAddr.sin_port = htons(broadcastPort);         /* Broadcast port */


           
      // Initialize I/O board
      if ( DMMinit() != 1) {
            printf("DMMinit failed.");
            exit(EXIT_FAILURE);
      }


//      DSCDACODE dacode;
//      DFLOAT zerovoltage = 0.0;
//      result = dscWGCommand(dscb,WG_CMD_PAUSE);
//      dscCancelOp(dscb);
//      result = dscVoltageToDACode( dscb, dscdasettings, zerovoltage, &dacode);
//      result = dscDAConvert( dscb, VOUTCH_LASER, (int)0);
//      dscSleep(2);  



      // Open MFC
      if ( setMFC( config.MFC ) != 1) {
            printf("setMFC failed.");
            exit(EXIT_FAILURE);
      }

//SetArduino Set Point
if( setSetPt( config.LSetPt ) != 1)
{
printf("Temperature Set Point Allocation Failed.");
exit(EXIT_FAILURE);
}

      createACScanRamp();
      createDCScanRamp();
      //result = ACscan();

      printf("Free disk space (MB): %f\n",getFreeDiskSpace());

DWORD start_time,end_time;

      do {      
        checkChunk();
        checkDisk();
	for( key = 0 ; key < 3 ; key ++ ) {

//		startWG();
//dscGetTime(&start_time);

		result = getHK();

//dscGetTime(&end_time);
//printf("End Time: %u\n",end_time-start_time);
//getchar();
		result = DCscan();
//		result = getHK();		

		if ( config.sendUDP == 1 ) 
		{
                  statusCt++;
                  if (statusCt > 100) statusCt = 0;
                  time_t init = time(NULL);
                  strftime(UDPtime,sizeof(UDPtime),"%Y%m%d%H%M%S",gmtime(&init));		
                  //ret = sprintf(sendString,"CUTW,%d,%.2f\n",statusCt,VMRraw);
                  ret = sprintf(sendString,"CUTWC,%s,%.2f,%.2f,%.2f,%.2f",UDPtime,rendpt,temp,pres,VMRraw);
                  //printf("%s",sendString);

                  sendStringLen = strlen(sendString);  /* Find length of sendString */
                   /* Broadcast sendString in datagram to clients*/  
                   if (sendto(sock, sendString, sendStringLen, 0, (struct sockaddr *)
                         &broadcastAddr, sizeof(broadcastAddr)) != sendStringLen)
                   {
                       printf("sendto() sent a different number of bytes than expected");
                       exit(EXIT_FAILURE);
                   }
        	 }

        }
      } while( 1 );

      // result = ACscan();
      
      // Release resources and shutdown
      prepareToExit();
      exit(EXIT_SUCCESS);
}

