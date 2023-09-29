/**
 * Author:        Bryan Rainwater
 * Created:       09/01/2020
 * Modified:      09/29/2023
 *
 * Contributors:  None
 * Acknowlegments:Basis for DAC/mods derived from Abishek Kakkar
 *                at https://github.com/abishek-kakkar/Beaglelogic
 *
 * Description:   Two channel fast Beaglebone Black ADC w/ realtime
 *                spectroscopic analysis, config, and data streams
 *
 **/

#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/poll.h>
#include <sys/errno.h>
#include <sys/mman.h>
#include <inttypes.h>
//#include <stdbool.h>
#include <signal.h>

#include <sys/types.h>
#include <sys/stat.h>
#include <sys/socket.h>
#include <fcntl.h>

#include <arpa/inet.h>
#include <netinet/in.h>

#include <math.h>


#include <time.h>
#include <unistd.h>

#include "libbeaglelogic.h"
#include "ini.h"

#include "mie.h"
#include "sqrt.h"


#define BEAGLELOGIC_SYSFS_ATTR(a)   "/sys/devices/virtual/misc/beaglelogic/"\
                                      __STRING(a)

static volatile sig_atomic_t keepRunning = 1;

int bfd, bstatefd;
int i, j, k;//, oversamp_i;
uint8_t *buf, *buf2, *buf3, *bufcppt, *bl_mem;

// The following defines must match the order in the INI file
#define HKIndex 0
#define logIndex 1
#define iniIndex 2
#define peakIndex 3
#define parsIndex 4
#define rawIndex 5
#define convIndex 6
#define diagIndex 7

/* For testing nonblocking IO */
#define NONBLOCK

#define readChunk 		4194304		// Chunk size of buffer address
#define availableFiles          8               // DO NOT EDIT

#define NUMBINS                 200

// Mie coefficient for log10(bit) as x, with coefficients a0*x^0, a1*x^1, ....
const float mieCoef[] = {-2413.7955928, 7212.0147781, -8200.5719334,\
    4749.2815734, -1467.1678222, 228.3945617, -13.7581998};

struct background {
    unsigned int baselinesHeld; // Number of actively held baselines

    // These are holding arrays for keeping track of background data	
    unsigned long int *bestDeviations; // Arr of abs vals diff of LPF and raw 
    unsigned int *bestBaselines;       // Arr of abs vals of window averages
    unsigned int *bestP2Ps;            // Arr of max - min in chosen baseline
    unsigned long long int *bestSkews; // Arr for assymetry of noise background
    unsigned long long int *bestKurts; // Arr for super/sub gaussian noise
    unsigned long long int *bestTimes; // Arr of time when baseline was stored.
    
    // Holding values for actively used baseline, std, and p2p
    unsigned int baseline;
    unsigned int std;
    unsigned int p2p;
    unsigned long int skew;
    unsigned long int kurt;
    unsigned long long int time;

    // Used to indicate where in the holding arrays the best value is
    int bestIndex;
    int worstIndex;

    // Accumulators for background intervals
    unsigned long long int varianceAccum; // Accumulator between intervals
    signed long long int skewAccum; // Accumulator between intervals
    unsigned long long int kurtAccum; // Accumulator between intervals
    unsigned long int baselineAccum; // Accumulator between intervals
    unsigned int max; // Used for defining max and min across baseline window
    unsigned int min; 
};


struct particle {
    unsigned int *ptr; // General ptr used for iterating across particle feature	
    unsigned int size; // Integer diameter of particle->
    unsigned long int peakAccum;// = 0; // Accumulator for averaging on peak

    // The following are pointers to where the value exists at
    unsigned int *lMin;      // Minima to the left of particle peak (ptr)
    unsigned int *rMin;      // Minima to the right of particle peak (ptr)
    unsigned int *peak;      // Index of held peak. // used for time stamp
    unsigned int *lHM;       //
    unsigned int *rHM;       //
    unsigned int *l3QM;      //
    unsigned int *r3QM;      //
    unsigned int convFlag;   // Flag if current particle possible convolut
    unsigned int convHist;   // Bool if last particle flagged as convolut

    unsigned int HMThresh;   //
    unsigned int TQMThresh;  //

    unsigned int peakWidth;  //
    //unsigned int  pAmp = 0;
    //unsigned int ch1pIntegral = 0;
};

struct histogram {
    unsigned int histBinEdges[NUMBINS+1];
    unsigned int histCnts[NUMBINS];
    unsigned int histMax;// = 0;
};

struct channel {
    unsigned int enable;

    unsigned int startFound;
    unsigned int endFound;
    unsigned int *startIndex;         // Ptr start of particle was flagged.
    unsigned int *endIndex;           // Ptr end of a particle was flagged.
    unsigned int startCnt; // Iter count points exceed LPF
    unsigned int startDropCtr;        // Iter accum # drops below LPF
    unsigned int indexToWaitUntil;    // When zero, no delay
    unsigned int backToBaselineCnt;   // Iter #pts back below baseline
    
    struct timespec startTime, endTime;
		
    unsigned int statSigCnt;  // Counting # particle pts at bsnln + 1sig
    unsigned int particleCnt;         // Iter when particle is found....

    unsigned int buffersDropped;      // # of buffers dropped before now
    
    unsigned int *buf, *lpf, *ptr, *lpfptr;

    // Used to hold data that carried over into the next buffer?
    unsigned int *buf_overflow;

    struct particle *particle;
    struct background *background;
    struct histogram *histogram;
};

struct fileSpecifics {
    // File setup info
    char suffix[15];
    FILE *fptr;
    unsigned long int fSize;
    unsigned int enable;
    unsigned int binary;
};

struct files {
    // Time at which last file check was made. Used to check if new file needed 
    struct fileSpecifics file[availableFiles];
    struct timespec lastFileTime;

    int lastFileDay;         // = 0; 
   
    char timeStamp[16];      // YYYYMMDDThhmmss
    char dateStamp[9];       // YYYYMMDD
    char pathBase[64];       // 
    char fileBase[64];       // 

    // Directory path for all subsequent files (should include y/m/d folders)
    char pathName[128];      // 
    
    unsigned int areActive;  // Changes to 1 when files have been initialized
    int version;             // Will increment up if need be

    int maxFileSize;         //
    int maxBinaryFileSize;   //

    int diagnosticSaveOption;
};

int UDPStat, UDP0R, UDP1S, UDP1R, UDP2S, UDP2R, UDPAC; // UDP references
struct UDP {
    char IP[sizeof(struct in6_addr)];   // IP address to connect to
    unsigned int port;                  // connection port
    char type[2];                       // S = Status, F = Full, A = Aircraft
    unsigned int use;                   // use this connection?
    struct sockaddr_in myaddr;          // address info
    struct sockaddr_in remaddr;         // address info
} UDP;

struct gUDP {
    struct UDP udp[6];
} gUDP;

char tmpStr[4094] = {""};
char udpPacket[4094] = {""};

int UDP0S;

struct measurement {
    unsigned int samplePeriod;
    unsigned int ch1Enable;
    unsigned int ch2Enable;
    float ch2GainScale;
    unsigned int simultaneous;
    unsigned int oversamp_bit;
    unsigned int pointSkip;
};

struct thresholds {
    unsigned int minStartPts;
    unsigned int maxStartDrops;
    unsigned int baselineWindow;
    unsigned int maxPtAge;
    unsigned int baselinesToHold;
    unsigned int backToBaselinePts;
    unsigned int LPFGain;
    unsigned int sigmaThreshold;
};

struct histograms {
    unsigned int numBins1;
    unsigned int miePolyOrder1;
    unsigned int pixMax1;
};

struct configuration { 
    // Substruct allocation
    struct measurement measurement;
    struct files files;
    struct thresholds thresholds;
    struct histograms histograms;
} cfg;

void fileSetup( int index, int option ) {
    char *suffixes[8] = {
        "HK",
        "LOG",
        "INI",
        "PK",
        "PARS",
        "RAW",
        "CONV",
        "DIAG",
    };
    switch(option) {
        case 0: 
            cfg.files.file[index].enable = 0;
            break;
        case 1: 
            cfg.files.file[index].enable = 1;
            cfg.files.file[index].binary = 0;
            break;
        case 2:
            cfg.files.file[index].enable = 1;
            cfg.files.file[index].binary = 1;
            break;
    }
    cfg.files.file[index].suffix[0] = '\0';
    strcat(cfg.files.file[index].suffix, suffixes[index]);
}


static int handler(void* user, const char* section, const char* name,
                   const char* value)
{
    struct configuration* pconfig = (struct configuration*)user;

    #define MATCH(s, n) strcmp(section, s) == 0 && strcmp(name, n) == 0

    if (MATCH("thresholds", "minStartPts")) {
        pconfig->thresholds.minStartPts = \
            (unsigned int)(atoi(value));
    } else if (MATCH("thresholds", "maxStartDrops")) {
        pconfig->thresholds.maxStartDrops = atoi(value);
    } else if (MATCH("thresholds", "baselineWindow")) {
        pconfig->thresholds.baselineWindow = atoi(value);
    } else if (MATCH("thresholds", "maxPtAge")) {
        pconfig->thresholds.maxPtAge = atoi(value);
    } else if (MATCH("thresholds", "baselinesToHold")) {
        pconfig->thresholds.baselinesToHold = atoi(value);
    } else if (MATCH("thresholds", "backToBaselinePts")) {
        pconfig->thresholds.backToBaselinePts = atoi(value);
    } else if (MATCH("thresholds", "LPFGain")) {
        pconfig->thresholds.LPFGain = atoi(value);
    } else if (MATCH("thresholds", "sigmaThreshold")) {
        pconfig->thresholds.sigmaThreshold = atoi(value);
    } 

    else if (MATCH("measurement", "oversampling")) {
        pconfig->measurement.oversamp_bit = atoi(value);
    } else if (MATCH("measurement", "pointSkip")) {
        pconfig->measurement.pointSkip = atoi(value);
    } else if (MATCH("measurement", "ch1Enable")) {
        pconfig->measurement.ch1Enable = atoi(value);
    } else if (MATCH("measurement", "ch2Enable")) {
        pconfig->measurement.ch2Enable = atoi(value);
    } else if (MATCH("measurement", "ch2GainScale")) {
        pconfig->measurement.ch2GainScale = atoi(value);
    } 
    
    else if (MATCH("files", "dataLocation")) {
        pconfig->files.pathBase[0] = '\0';
        strcat(pconfig->files.pathBase, value);
    } else if (MATCH("files", "maxFileSize")) {
        pconfig->files.maxFileSize = atoi(value);
    } else if (MATCH("files", "maxBinaryFileSize")) {
        pconfig->files.maxBinaryFileSize = atoi(value);
    } else if (MATCH("files", "diagnosticSaveOption")) {
        pconfig->files.diagnosticSaveOption = atoi(value);
    } else if (MATCH("files", "saveHK")) {
        fileSetup( 0, atoi(value) );
    } else if (MATCH("files", "saveLog")) {
        fileSetup( 1, atoi(value) );
    } else if (MATCH("files", "saveIni")) {
        fileSetup( 2, atoi(value) );
    } else if (MATCH("files", "savePeakHeights")) {
        fileSetup( 3, atoi(value) );
    } else if (MATCH("files", "saveParticleParams")) {
        fileSetup( 4, atoi(value) );
    } else if (MATCH("files", "saveRawParticles")) {
        fileSetup( 5, atoi(value) );
    } else if (MATCH("files", "saveConvolvedParticles")) {
        fileSetup( 6, atoi(value) );
    } else if (MATCH("files", "saveDiagnosticStream")) {
        fileSetup( 7, atoi(value) );
    }

    else {
        return 0;  /* unknown section/name, error */
    }
    return 1;
}


// DO NOT want to pass dir by reference
int mkdirp(const char *originalPath, mode_t mode) {
    // First attempt with mkdir at largest directory
    // If fails, split string, recursively try again, once it returns,
    //   add last token back on, try again. If it fails again, return -1
    // otherwise return 0.
    errno = 0;
   
    char dir[128] = "";
    strcat( dir, originalPath );
    printf("Directory in mkdirp: %s\n", dir);
    if( mkdir(dir, mode) && errno != EEXIST  ) {
        // Returned -1 indicating failure.
        // ATTENTION: try remove last token from string, recursively try again       
        // create holding array for trailing token 
        char trailingDir[128] = "";

        // Returns pointer containing /lastToken
        char *last = strrchr(dir, '/');
       
        // If last is == NULL, then nothing exists to remove, return failure
        if (last == NULL ) {
           return -1;
        }
        else {
            // Now storing last token to trailingDir
            strcat(trailingDir, last);
   
            // Removes trailingDir from dir
            dir[strlen(dir) - strlen(last)] = '\0';
 
            printf("Directory in mkdirp after strip: %s\n", dir);
            // Try again, needs to be recursive
            if( mkdirp(dir, mode) ) {
                // Because of second failure, unsure of cause, return failure
                return -1;
            }
            else {
                // since one up directory succeeded, add back on original tail
                strcat(dir,trailingDir);
                printf("Directory in mkdirp after readd: %s\n", dir);
                return mkdirp(dir, mode);
            }
        }
    }
    return 0;
}

void closeFiles() {
    int fileNum = 0;
    for( fileNum = 0; fileNum < availableFiles; fileNum++ ) {
        if( cfg.files.file[fileNum].fptr != NULL ) {
            fclose( cfg.files.file[fileNum].fptr );
        }
    }

}

int parseDate( time_t seconds, char *year, char *month, char *day, unsigned int *time ) {
    struct tm *gmtNow;
    gmtNow = gmtime(&seconds);

    sprintf(year, "%04d",(gmtNow->tm_year+1900));
    sprintf(month, "%02d", (gmtNow->tm_mon+1));
    sprintf(day, "%02d", (gmtNow->tm_mday));

    time[0] = gmtNow->tm_hour;
    time[1] = gmtNow->tm_min;
    time[2] = gmtNow->tm_sec;

    // Just used for day comparison for new file creation
    return gmtNow->tm_mday;
}

/***************************************************************************//**
 * File Management Function
 *
 * This function acts to handle all file management operations such as creation,
 * folder structure, versioning, timing, etc. To be run at program startup for
 * initial file creation and after each buffer completion to check if new files
 * need to be created.
 *
 ******************************************************************************/
void fileMgmt() {
    // Iterator through available file options
    int fileNum = 0;
    // Check file sizes 
    struct timespec prospectiveFileTime; 
    char activeFile[64] = "";
    char tmpFileStr[10] = "";
    struct stat st;
    int status;

    unsigned int time[3]; //contains year, month, day vals
    char year[5] = "";
    char month[3] = "";
    char day[3] = "";

    // Initialize timing schema
    clock_gettime(CLOCK_REALTIME, &prospectiveFileTime);

    // Now use this time and date to allocate yyyy/mm/dd folders 
    parseDate( prospectiveFileTime.tv_sec, year, month, day, time );

    // If files are not active yet, need to activate them...
    if ( !cfg.files.areActive ) {
        cfg.files.lastFileTime = prospectiveFileTime;
        cfg.files.lastFileDay = atoi(day);
        cfg.files.pathName[0] = '\0';
        strcat( cfg.files.pathName, cfg.files.pathBase );
        strcat( cfg.files.pathName, "/");
        printf("%s",year);
        strcat( cfg.files.pathName, year);
        strcat( cfg.files.pathName, "/");
        strcat( cfg.files.pathName, month );
        strcat( cfg.files.pathName, "/");
        strcat( cfg.files.pathName, day );
        strcat( cfg.files.pathName, "/");

        sprintf( cfg.files.fileBase, "%s%s%sT%02d%02d%02d_", \
            year, month, day, time[0], time[1], time[2]);

        // Initialize recursive directory structure based on date/time
        // USE mkdir -p for non error recursive directory creation
        // Needs to be recursive
        //mkdirp( cfg.files.pathName, 0666 );
        printf("Intended file path: %s\n", cfg.files.pathName);
        
        mkdirp( cfg.files.pathName, 0666 );

        for ( fileNum = 0; fileNum < availableFiles; fileNum++ ) {
            if ( cfg.files.file[fileNum].enable ) {
                // Create filename
                //sprintf( activeFile, "" );
                activeFile[0] = '\0';
                strcat( activeFile, cfg.files.pathName );
                strcat( activeFile, cfg.files.fileBase );
                strcat( activeFile, cfg.files.file[fileNum].suffix );
                strcat( activeFile, "_" );
                    
                sprintf( tmpFileStr, "x%03d", cfg.files.version ); 

                strcat( activeFile, tmpFileStr);
  
                switch ( cfg.files.file[fileNum].binary ) {
                    case 0:
                        strcat( activeFile, ".csv" );
                        break;
                    default:
                        strcat( activeFile, ".bin" );
                        break;
                }

                printf("Intended file: %s\n", activeFile);

                // Now that file name has been identified, check if exists
                //   if exists, increment version, recursively run fcn again
                status = stat(activeFile, &st);

                if(status == 0) {
                    //if (st.st_size >= 51200000)
                    cfg.files.version++;
                    fileMgmt();
                }
                else {
                    // If fptr exists, close it first....
                    if( cfg.files.file[fileNum].fptr ) {
                        fclose(cfg.files.file[fileNum].fptr);
                    }
                    // Now that we are on correct filename, open file ptrs
                    switch ( cfg.files.file[fileNum].binary ) {
                        case 0:
                            cfg.files.file[fileNum].fptr = \
                                fopen(activeFile, "w"); 
                            break;
                        default: 
                            cfg.files.file[fileNum].fptr = \
                                fopen(activeFile, "w");
                            break;
                    }
                }
            }
        }

        // Denote files are now active and ready to write
        cfg.files.areActive = 1;//true;

        // Given that this was a file creation routine, we DO NOT
        //   need to run subsequent code for checking if new day
        return;

    }

    // FIRST check to see if new write time is on a new day, if so, recursive
    if ( atoi(day) != cfg.files.lastFileDay ) {
        cfg.files.version++;
        cfg.files.areActive = 0;//false;
        fileMgmt();
    }
       
    // Now that files are ready to write, check if too big
    for( fileNum = 0; fileNum < availableFiles; fileNum++ ) {
        // Checks if file is to be written to, if not, continue loop
        if( !cfg.files.file[fileNum].enable ) {
            continue;
        }
        // Check file status of open file descriptor
        status = fstat(fileno(cfg.files.file[fileNum].fptr), &st);
        switch ( cfg.files.file[fileNum].binary ) {
            case 0:
                if( st.st_size >= cfg.files.maxBinaryFileSize ) {
                    cfg.files.version++;
                    cfg.files.areActive = 0;//false;
                    fileMgmt();
                }
                break;
            default:
                if( st.st_size >= cfg.files.maxFileSize ) {
                    cfg.files.version++;
                    cfg.files.areActive = 0;//false;
                    fileMgmt();
                }
                break;
        }
    }
}

/***************************************************************************//**
 * File Save Function
 *
 * This function performs save operations based on channel struct
 *
 ******************************************************************************/
void fileSave(struct channel **ch, int saveType) {
    // Note the ** implies pass struct pointer by reference, NOT as a copy
    // saveType is either 0 for broadloop save, or 1 for immediate (particle)

    //"HK",
    //"LOG",
    //"INI", // Handled by fileMgmnt on new file creation
    //"PK", // Instant
    //"PARS", // Instant
    //"RAW", // Instant
    //"CONV", // Instant
    //"DIAG", // 

    switch(saveType) {
        case 1: // This is for immediate particle saves
            
        default:  // This is the broadloop save
            // First perform fileMgmnt
            fileMgmt();

            // Now move on, check if specific save is enabled, save accordingly
    }
    // First check save type....
    // If HK, merge data
}

//******************************************************************************
//
//  Write_UDP
//
//  Writes message to a UDP socket
//			
//  Parameters: int fd (UDP reference)
//				int i (udp index)
//				char msg[] (message to write)
//
//  Returns: int slen (string length)
//				
//******************************************************************************

int Write_UDP(int udpfd, int udpNum, char msg[])
{
    int slen=sizeof(gUDP.udp[udpNum].remaddr);

    if (strlen(msg) > 0) {
        if (sendto(udpfd, msg, strlen(msg), 0, \
            (struct sockaddr *)&gUDP.udp[udpNum].remaddr, slen)==-1) {
                //sprintf(str,"Error with UDP sendto %d\n",i);   
                // it's just that there is no listener.
        }
    }
    return slen;
}

//******************************************************************************
//
//  Open_Socket_Write
//
//  Opens a UDP socket for write
//			
//  Parameters: int i (UDP index)
//
//  Returns: int fd (UDP reference)
//				
//******************************************************************************
 
int Open_Socket_Write(int udpNum)
{
    int udpfd;
    /* create a socket */

    if ( ( udpfd=socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP ) ) <0)
	printf("Socket creation error\n");

    /* now define remaddr, the address to whom we want to send messages */
    /* For convenience, the host address is expressed as a numeric IP address */
    /* that we will convert to a binary format via inet_aton */
    memset((unsigned char *) &gUDP.udp[udpNum].remaddr, 0, \
        sizeof(gUDP.udp[udpNum].remaddr));
    gUDP.udp[udpNum].remaddr.sin_family = AF_INET;
    gUDP.udp[udpNum].remaddr.sin_port = htons(gUDP.udp[udpNum].port);
    if (inet_pton(AF_INET, gUDP.udp[udpNum].IP, \
        &gUDP.udp[udpNum].remaddr.sin_addr)==0) {
            printf("Write socket inet_aton() failed\n");
            return 0;
    }
    return udpfd;
}

//******************************************************************************
//
//  Close_UDP_Socket
//
//  Closes a UDP socket
//				
//  Parameters: int (reference to the UDP socket)
//
//  Returns:	void
//				
//******************************************************************************
 
void Close_UDP_Socket(int UDPID)
{
    close(UDPID);
}

/* Returns time difference in microseconds */
static uint64_t timediff(struct timespec *tv1, struct timespec *tv2)
{
    return ((((uint64_t)(tv2->tv_sec - tv1->tv_sec) * 1000000000) +
        (tv2->tv_nsec - tv1->tv_nsec)) / 1000);
}


int waitForNextBuffer(void) {
    bstatefd = open(BEAGLELOGIC_SYSFS_ATTR(state), O_RDONLY);
    char statebuf[16];
    char *endptr;
    int nextbuf, ret;

    if (!bstatefd)
        return -1;

    if ((ret = read(bstatefd, statebuf, 16)) < 0)
        return -1;

    close(bstatefd);
    // Rainwater edit 03312023 for 10 -> 12 bit conversion
    nextbuf = strtoul(statebuf, &endptr, 10);// 12);//10);

    return nextbuf;
}

unsigned int int16sqrt(unsigned int n) {

    unsigned int save = 0;
    unsigned int g = 0x8000;
    unsigned int c = 0x8000;
    do {
        if (g*g > n)       //-- Intermediate root too high?
            g = save;      //-- Get last guess with current bit cleared.
        else {
            save = g;      //-- Save current guess before setting next bit.
        }
        c >>= 1;
        g |= c;            //-- Insert 1-bit.
    } while (c != 0); 
    return g;              //-- Final root may not be floor[√n].
}

/* Handles SIGINT */
void exithandler(int x)
{
    if (buf)
        free(buf);

    printf("sigint caught\n");
    fflush(stdout);
    beaglelogic_close(bfd);

    exit (-1);
}

/* Handles SIGSEGV */
void segfaulthandler(int x)
{
    printf("segfault caught at i = %X\n", i);

    fflush(stdout);
    beaglelogic_close(bfd);

    if (buf)
        free(buf);

    exit (-1);
}

int main(int argc, char **argv)
{
    strcpy(gUDP.udp[0].IP, "192.168.7.1");
    gUDP.udp[0].port = 10080;
    strcpy(gUDP.udp[0].type, "F");
    gUDP.udp[0].use = 1;//true;
    UDP0S = Open_Socket_Write(0);

    int sz;
    size_t cnt1, sz_to_read; // sz
    size_t ch_sz, oversamp_sz;

    // Temporary variables for holding
    unsigned long long int tmpGausVar = 0;
    // minimizerOption 5 is p2p*var
    unsigned int minimizerOption = 5; //0 = p2p, 1 = var, 2 = skew, 3 = kurt

    // Buffer index is denoted by division of total
    //	buffer among 4MB chunks....
    // So if 12MB buffer, bufferAlternator will cycle
    //	between 0, 1, and 2.
    // Detect if buffer was dropped by reading in 4MB chunks

    // Pull configuration data
    if (ini_parse("/home/debian/main.ini", handler, &cfg) < 0) {
       	printf("Can't load 'main.ini'\n");
       	return 1;
    }
    printf("Ini configuration option: %u\n",\
        cfg.thresholds.minStartPts);

    fileMgmt();

    // Global buffer counter
    unsigned long int buffersRead = 0;
	
    // Number of 4MB buffer blocks being stored to
    unsigned int bufferBlocks = 0;
	
    // Most recent buffer number read
    unsigned int bufferAlternator = 0; 
    unsigned int lastBufferRead = 0;

    /**
     * Histogram plotting on command line
     *     double histBinEdges[NUMBINS+1];
     *       = [1,1.2,1.4,1.6,1.8,2.0,2.2,2.4,2.6,2.8,3.0,3.2,3.4]
     * unsigned int histPixels[NUMBINS];
     * uint16_t histCnts{13};
     *
     * Particle Buffer (for histogramming, etc.)
     *
     * Gaussian noise array....
     * srand(time(0));
     * Rand will now produce value between 0 and 32767
     * So bit shift this down a 8 bits to drop 0 to 128
     * 
     * int noiseAmp = 64;
     * int signalAmp = 1000;
     * int signalWidth = 4;
     * int signalDelay = 1024*128;
     **/

    unsigned int onDivision = 0; // Used for checking division of 
    
    unsigned int zeroIntervalFlag = 0; // Only when ==1 can things accumulate
    // Used to restrict accumulation away from edges of buffer
    
    //////////////////////////////////////////////////////////////////////////
    //		     VARIABLES FOR PARTICLE ANALYSIS			//
    //////////////////////////////////////////////////////////////////////////
    unsigned long long int globalLoopCt = 0;

    struct timespec t1, t2;
    struct timespec compt1, compt2, readt1, readt2, bufwaitt1, bufwaitt2;

    /* Open BeagleLogic */
    clock_gettime(CLOCK_MONOTONIC, &t1);
    bfd = beaglelogic_open_nonblock();

    clock_gettime(CLOCK_MONOTONIC, &t2);

    if (bfd == -1) {
        printf("BeagleLogic open failed! \n");
        return -1;
    }

    //printf("BeagleLogic opened successfully in %jd us\n",

    /* Memory map the file */
    bl_mem = beaglelogic_mmap(bfd);

    /* Register signal handlers */
    signal(SIGINT, exithandler);
    signal(SIGSEGV, segfaulthandler);

    /* Configure buffer size - we need a minimum of 32 MB */
    beaglelogic_get_buffersize(bfd, &sz_to_read);

    bufferBlocks = sz_to_read/(4*1024*1024);
    // Rainwater edit 03312028
    sz_to_read /= bufferBlocks;
    printf("Number of 4MB buffer blocks: %u\n", bufferBlocks);
    
    // Each channel is two bytes, so per channel size is (4 times smaller) 
    ch_sz = sz_to_read/4;
    
    int oversamp_i = 0; 
    unsigned int oversamp_jmp = (1<<cfg.measurement.oversamp_bit);
    // This will define how large the lpf array is....
    //   when oversamp_bit == 0, don't divide
    //   when oversamp_bit == 1, divide by 2
    //   when oversamp_bit == 2, divide by 4
    //   when oversamp_bit == 3, divide by 8
    oversamp_sz = ch_sz/(1<<cfg.measurement.oversamp_bit);
   
    printf("Channel Size and Oversample Size: %zu and %zu\n", \
        ch_sz, oversamp_sz);

    buf = calloc(sz_to_read, sizeof(uint8_t));
    memset(buf, 0xFF, sz_to_read);

    int chNum = 0;

    // Struct members are initialized to zero, ptrs to nil
    struct channel *ch;
    ch = (struct channel*) calloc(2, sizeof(struct channel));

    //bestStd, ... may need to be initialized to something non zero
    for ( chNum = 1; chNum >= 0; chNum-- ) {
        (ch + chNum)->background = \
            (struct background*)calloc(1, sizeof(struct background));
        (ch + chNum)->particle = \
            (struct particle*)calloc(1, sizeof(struct particle));
        (ch + chNum)->histogram = \
            (struct histogram*)calloc(1, sizeof(struct histogram));

        (ch + chNum)->background->bestDeviations = \
            calloc(cfg.thresholds.baselinesToHold,sizeof(unsigned long int));
        (ch + chNum)->background->bestBaselines = \
            calloc(cfg.thresholds.baselinesToHold,sizeof(unsigned int));
        (ch + chNum)->background->bestP2Ps = \
            calloc(cfg.thresholds.baselinesToHold,sizeof(unsigned int));
        (ch + chNum)->background->bestSkews = \
            calloc(cfg.thresholds.baselinesToHold, \
            sizeof(unsigned long long int));
        (ch + chNum)->background->bestKurts = \
            calloc(cfg.thresholds.baselinesToHold,\
            sizeof(unsigned long long int));
        (ch + chNum)->background->bestTimes = \
            calloc(cfg.thresholds.baselinesToHold,\
            sizeof(unsigned long long int));
        (ch + chNum)->background->bestIndex  = -1;
        (ch + chNum)->background->worstIndex = -1;
        
        (ch + chNum)->buf = calloc(oversamp_sz, sizeof(unsigned int));
        (ch + chNum)->lpf = calloc(oversamp_sz, sizeof(unsigned int));
        
        (ch + chNum)->particle->lMin = \
            (ch + chNum)->particle->lHM = \
            (ch + chNum)->particle->l3QM = \
            (ch + chNum)->particle->peak = \
            (ch + chNum)->particle->r3QM= \
            (ch + chNum)->particle->rHM = \
            (ch + chNum)->particle->rMin = \
            (ch + chNum)->lpf;

        (ch + chNum)->particle->peakWidth = 1;

        (ch + chNum)->background->baseline = 65535;
        (ch + chNum)->background->std = 65535;
        (ch + chNum)->background->p2p = 65535;
        (ch + chNum)->background->skew = 4194304;
        (ch + chNum)->background->kurt = 4194304;
        (ch + chNum)->background->time = 0;   
 
        for(j=0; j<NUMBINS+1; j++) {
            (ch + chNum)->histogram->histBinEdges[j] = \
                (unsigned int)(0.0 + ((32768.0)/\
                ((double)(NUMBINS))*((double)(j))));
        }
        (ch + chNum)->histogram->histBinEdges[NUMBINS] = 65535;
    }
    ch[0].enable = cfg.measurement.ch1Enable;//0;
    ch[1].enable = cfg.measurement.ch2Enable;//

    if( cfg.files.file[parsIndex].enable ) {
        fprintf(cfg.files.file[parsIndex].fptr,"Time(s), Time(ns), gLpCtr, ");
        fprintf(cfg.files.file[parsIndex].fptr,"bsln, bstd, bP2P, lHght, ");
        fprintf(cfg.files.file[parsIndex].fptr,"lHWHM,lHW3QM,Peak,rHW3QM, ");
        fprintf(cfg.files.file[parsIndex].fptr, "rHWHM,rHght,convFlag\n");
    }	

    printf("Buffer size = %d MB \n", bufferBlocks * sz_to_read / (1024 * 1024));

    /* All set, start a capture */
    clock_gettime(CLOCK_MONOTONIC, &t1);
    bufferAlternator = waitForNextBuffer();
    lastBufferRead = bufferAlternator;

    size_t buf_i;
    while(keepRunning) {
        //Check time before doing anything....
        clock_gettime(CLOCK_MONOTONIC, &t1);
       
        // Reset histogram counting
        for(i=0; i<NUMBINS; i++) {
            ch->histogram->histCnts[i] = 0;
            (ch+1)->histogram->histCnts[i] = 0;
        }

        /* Configure counters */
        cnt1 = 0; // Used to just count when done reading sz to read
        buf2 = buf; // Set to beginning of buffer
        // Testing to be smaller than size of bl_mem
		
        buf3 = bl_mem;
		
        buf3 = bufferAlternator != bufferBlocks - 1 ? bl_mem + \
            (bufferAlternator<<22) : bl_mem;
		
        clock_gettime(CLOCK_MONOTONIC, &readt1);
        // ~15ms 64KB buffer read chunks blocking
        // ~13ms 4MB buffer read as a single chunk blocking
                
        sz = read(bfd, NULL, readChunk);
        buffersRead++;

        clock_gettime(CLOCK_MONOTONIC, &readt2);

        clock_gettime(CLOCK_MONOTONIC, &compt1);
    
        ch->particleCnt = 0;
        (ch+1)->particleCnt = 0; 
        ch->buffersDropped = 0;
        (ch+1)->buffersDropped = 0;

        // Buffer (bufcppt+= n) where n must be decided by the oversamp_bit, 
        for ( buf_i = oversamp_sz, ch->ptr = ch->buf, (ch+1)->ptr =(ch+1)->buf,\
            ch->lpfptr = ch->lpf, (ch+1)->lpfptr = (ch+1)->lpf, bufcppt=buf3; \
            buf_i; (ch->ptr)++, ((ch+1)->ptr)++, (ch->lpfptr)++, \
            ((ch+1)->lpfptr)++, bufcppt+=(4<<cfg.measurement.oversamp_bit)<<\
            (cfg.measurement.pointSkip), buf_i-=1<<cfg.measurement.pointSkip, \
            globalLoopCt++) {
            
            //Tracks total #pts processed, for checking stale baselines

            // cfg.measurement.pointSkip denotes how many points to skip
	
            for( chNum = 1; chNum >= 0; chNum-- ) {
                for ( *((ch + chNum)->ptr) = 0, oversamp_i = oversamp_jmp - 1;\
                    oversamp_i >= 0; oversamp_i-- ) {
                        // Now add progressively more bits
                        *((ch + chNum)->ptr) += *(bufcppt + 1 + \
                            (oversamp_i<<2) + (chNum<<1) )<<8 ;
                        *((ch + chNum)->ptr) += *(bufcppt +  (oversamp_i<<2) + \
                            (chNum<<1) );                
                } 
                // When bit_oversample = 0, upscale 6 bits, 
                // when =1, upscale 5 bits, when 2, upscale 4 bits 
                //*((ch + chNum)->ptr) <<= (6 - cfg.measurement.oversamp_bit);
                // Rainwater edit 03312023, 10 -> 12 bit modification
		*((ch + chNum)->ptr) <<= (4 - cfg.measurement.oversamp_bit);
           
                //Begin LPF translation:
                if((ch + chNum)->ptr == (ch + chNum)->buf) {
                    *((ch + chNum)->lpfptr) = *((ch + chNum)->ptr);
                }
                else {
                    *((ch + chNum)->lpfptr) = \
                        (( *((ch + chNum)->lpfptr - 1) << \
                        cfg.thresholds.LPFGain ) - \
                        (*((ch + chNum)->lpfptr - 1)) + \
                        (*((ch + chNum)->ptr)) ) >> cfg.thresholds.LPFGain;
                }
            }
            
            // Add random noise....
            //printf("Random value: %d, %d\n", rand(), rand()%64);
            //*ch1pt += rand()%noiseAmp;
            //*(ch[1].ptr += rand()%128;
				
            // Particle simulated addition....
            //	Modulo creation. I.e. a gaussian particle of 
            //  amplitude 200 bits and 15 width would be
            // 	a switch statment addition

            //for(j = -signalWidth*4; j<=signalWidth*4; j++) {
            //	if ( (globalLoopCt + j) % signalDelay == 0 ) *ch1pt += \
            //  exp((-j*j/(2*signalWidth*signalWidth)))*signalAmp;
            //}

		
            ////////////////////////////////////////////////////////////////////
            /*                        BEGIN BASELINE CODE                     */
            ////////////////////////////////////////////////////////////////////


            // Baseline approach: 
            //   Rolling arrays containing up to, say, 5, baselines, 
            //     with worstIndex being the
            //   index that contains the ready to discard data

            // Modulo notes, Modulo is slow compared to bitwise and, 
            //   the following hold true
            //	ONLY WITH POWERS OF TWO MODULO
            //	x % 2 == x & 1
            //	x % 4 == x & 3
            //	x % 8 == x & 7
            //
            onDivision = ( ( globalLoopCt & ( ( 1 << \
                cfg.thresholds.baselineWindow ) - 1 ) ) > 0) ? 0: 1;

            // First check to make sure we are NOT on proper division of buffer
            //    to analyze and not on edges... ONLY THEN, do we allow 
            //    accumulator to be filled, WHEN zeroIntervalFlag allows it           
            if ( !onDivision && zeroIntervalFlag) {
                //Fill accum only once accumulator has accumulated
                for( chNum = 1; chNum >= 0; chNum-- ) {
                    tmpGausVar = \
                        ((*((ch + chNum)->lpfptr))*(*((ch + chNum)->lpfptr))) +\
                        ((*((ch + chNum)->ptr))*(*((ch + chNum)->ptr))) - \
                        (((*((ch + chNum)->lpfptr))*(*((ch + chNum)->ptr)))<<1);
                    
                    // Now store variance to variance accumulator
                    (ch + chNum)->background->varianceAccum += tmpGausVar;

                    // Skew is + (meas-act)^3  
                    //(ch + chNum)->background->skewAccum += \
                        tmpGausVar * ( (int)(*(ch + chNum)->ptr) - \
                        (int)(*(ch+chNum)->lpfptr) );
                    
                    // Kurt is + (meas-act)^4 = var^2
                    //(ch + chNum)->background->kurtAccum += \
                        (tmpGausVar*tmpGausVar);

                    // Just add, will divide down later
                    (ch + chNum)->background->baselineAccum += \
                        *((ch + chNum)->ptr);
  		 
                    if( *((ch + chNum)->ptr) > (ch + chNum)->background->max ) {
                        (ch + chNum)->background->max = \
                            *((ch + chNum)->ptr);//LPFptr;
                    }
                    if( *((ch + chNum)->ptr) < (ch + chNum)->background->min ) {
                        (ch + chNum)->background->min = \
                            *((ch + chNum)->ptr);//LPFptr;
                    }
                }
            }

            // Second check to see if ready to be analyzed on 
            //   specific interval && zeroIntervalFlag allows it
            if ( onDivision && zeroIntervalFlag ) {
                for ( chNum = 1; chNum >= 0; chNum-- ) {
                    // Divide down the Accumulators to appropriate value
                    (ch + chNum)->background->baselineAccum >>= \
                        cfg.thresholds.baselineWindow;
                    (ch + chNum)->background->varianceAccum >>= \
                        ( cfg.thresholds.baselineWindow ); // (N-1) vs N.
                    
		    /* 
                    if ( (ch+chNum)->background->varianceAccum != 0 && \
                        (ch+chNum)->background->varianceAccum <= 4000000) {
                            (ch + chNum)->background->skewAccum /= \
                                ( cfg.thresholds.baselineWindow ); 
                            (ch + chNum)->background->skewAccum /= \
                                (ch + chNum)->background->varianceAccum;
                            (ch + chNum)->background->skewAccum /= \
                                SQRTTBL[(ch + chNum)->background->varianceAccum];
                            (ch + chNum)->background->skewAccum = \
                                llabs((ch + chNum)->background->skewAccum);
                    } 
                    else {
                        (ch + chNum)->background->skewAccum = 4194304;
                    }
		    */

                    //(ch + chNum)->background->kurtAccum /= \
                    //    (ch+chNum)->background->varianceAccum;
                    //(ch + chNum)->background->kurtAccum /= \
                        (ch+chNum)->background->varianceAccum;
                    //(ch + chNum)->background->kurtAccum -= 3;

                    // Minimum bit noise requiremenpt
                
		    // Rainwater edit 03312023, 10 -> 12 bit modification
                    if ( (ch + chNum)->background->varianceAccum == 0 ) {
                        (ch + chNum)->background->varianceAccum = \
                            (1<<(4 - cfg.measurement.oversamp_bit));//>>1;//4;
                        if ( (ch + chNum)->background->varianceAccum == 0 ) {
                            (ch + chNum)->background->varianceAccum = 1;//4;
                        }
                    }
		    
		    // Rainwater edit 03312023, 10 -> 12 bit modification
                    if ( (ch + chNum)->background->min == \
                        (ch + chNum)->background->max ) {
                            (ch + chNum)->background->max += \
                                1<<(4-cfg.measurement.oversamp_bit);//16;
                    }
                    
                    // First, if at least one elements held, 
                    //   begin cutting off points until young enough
                    // j>=0 because we are okay with losing oldest point 
                    //   (this will replace with newest).
                    //	NOTE: If it ever reaches this, 
                    //  maxAge needs to be increased.
                    if ( (ch + chNum)->background->baselinesHeld > 0 ) {
                        //Init best and worsts here as the last element in array
                        (ch + chNum)->background->bestIndex = \
                            (ch + chNum)->background->baselinesHeld - 1; 
                        (ch + chNum)->background->worstIndex = \
                            (ch + chNum)->background->baselinesHeld - 1;
                        for (j = (ch + chNum)->background->baselinesHeld - 1; j>=0; j--) { 
                            if ( globalLoopCt - *( (ch + chNum)->background->bestTimes + j ) > (1<<cfg.thresholds.maxPtAge) ) {
                                printf("Deemed some value has become too old\n");
                                (ch + chNum)->background->baselinesHeld = j;
                                (ch + chNum)->background->bestIndex = j-1;
                                (ch + chNum)->background->worstIndex = j-1;
                            }
                            else { 
                                // Find new best and worsts
                                // The above If SHOULD have allocated chxBest and Worst appropriately
                                //	To be the last non overage element. This else then cycles to find best and worst.
                                // Gradually update best.
                                //	Note: "<=" and ">=" for ensuring that the best is always newer if identical
                                
                                switch ( minimizerOption ) {
                                    case 0: // p2p
                                        if ( *( (ch + chNum)->background->bestP2Ps + j ) <= *( (ch + chNum)->background->bestP2Ps + \
                                            (ch + chNum)->background->bestIndex ) ) {
                                                (ch + chNum)->background->bestIndex = j;
                                         }
                                         // Gradually update worst. Basically searching for worst (">") because we want
                                         //	oldest worst to be replaced
                                         if ( *( (ch + chNum)->background->bestP2Ps + j ) > *( (ch + chNum)->background->bestP2Ps + \
                                             (ch + chNum)->background->worstIndex ) ) {
                                                 (ch + chNum)->background->worstIndex = j;
                                         }
                                         break;
                                    case 1: // variance
                                        if ( *( (ch + chNum)->background->bestDeviations + j ) <= *( (ch + chNum)->background->bestDeviations + \
                                            (ch + chNum)->background->bestIndex ) ) {
                                                (ch + chNum)->background->bestIndex = j;
                                         }
                                         // Gradually update worst. Basically searching for worst (">") because we want
                                         //	oldest worst to be replaced
                                         if ( *( (ch + chNum)->background->bestDeviations + j ) > *( (ch + chNum)->background->bestDeviations + \
                                             (ch + chNum)->background->worstIndex ) ) {
                                                 (ch + chNum)->background->worstIndex = j;
                                         }
                                         break;
                                    /*
                                    case 2: // skew
                                         if ( *( (ch + chNum)->background->bestSkews + j ) <= *( (ch + chNum)->background->bestSkews + \
                                            (ch + chNum)->background->bestIndex ) ) {
                                                (ch + chNum)->background->bestIndex = j;
                                         }
                                         // Gradually update worst. Basically searching for worst (">") because we want
                                         //	oldest worst to be replaced
                                         if ( *( (ch + chNum)->background->bestSkews + j ) > *( (ch + chNum)->background->bestSkews + \
                                             (ch + chNum)->background->worstIndex ) ) {
                                                 (ch + chNum)->background->worstIndex = j;
                                         }
                                         break;
                                    case 3: // kurt
                                         if ( *( (ch + chNum)->background->bestKurts + j ) <= *( (ch + chNum)->background->bestKurts + \
                                            (ch + chNum)->background->bestIndex ) ) {
                                                (ch + chNum)->background->bestIndex = j;
                                         }
                                         // Gradually update worst. Basically searching for worst (">") because we want
                                         //	oldest worst to be replaced
                                         if ( *( (ch + chNum)->background->bestKurts + j ) > *( (ch + chNum)->background->bestKurts + \
                                             (ch + chNum)->background->worstIndex ) ) {
                                                 (ch + chNum)->background->worstIndex = j;
                                         }
                                         break;
                                    */
                                    default: // p2p*var
                                        if ( *( (ch + chNum)->background->bestP2Ps + j ) * (*(ch+chNum)->background->bestDeviations + j) <= \
                                             *( (ch + chNum)->background->bestP2Ps + (ch + chNum)->background->bestIndex ) * \
                                             (*( (ch + chNum)->background->bestDeviations + (ch + chNum)->background->bestIndex) ) ) {
                                                    (ch + chNum)->background->bestIndex = j;
                                         }
                                         // Gradually update worst. Basically searching for worst (">") because we want
                                         //	oldest worst to be replaced
                                         if ( *( (ch + chNum)->background->bestP2Ps + j ) * (*(ch+chNum)->background->bestDeviations + j) > \
                                             *( (ch + chNum)->background->bestP2Ps + (ch + chNum)->background->worstIndex ) * \
                                             (*( (ch + chNum)->background->bestDeviations + (ch + chNum)->background->worstIndex) ) ) {
                                                 (ch + chNum)->background->worstIndex = j;
                                         }
                                         break;
                                }
                            }						
                        }					
                    }
				
                    // Now, long as there is still data in the array, we update best vs worst by comparing to newest point
                    switch ( minimizerOption ) {
                        case 0: // p2p
                            if ( (ch + chNum)->background->baselinesHeld > 0 ) {
                                // This condition means new variance is lower (better) than the best in the old data
                                if ( (ch + chNum)->background->max - (ch + chNum)->background->min  <= *( (ch + chNum)->background->bestP2Ps + \
                                    (ch + chNum)->background->bestIndex ) ) {
                                        (ch + chNum)->background->bestIndex = -1; // Denotes best is new value
                                }
                                // This condition means new value is worse than the worst. So don't shift unless we have to.
                                if ( (ch + chNum)->background->max - (ch + chNum)->background->min > *( (ch + chNum)->background->bestP2Ps + \
                                    (ch + chNum)->background->worstIndex ) ) {
                                        (ch + chNum)->background->worstIndex = -1; //(ch + chNum)->background->baselinesHeld-1;
                                }
                            }
                            break;
                        case 1: // variance
                            if ( (ch + chNum)->background->baselinesHeld > 0 ) {
                                // This condition means new variance is lower (better) than the best in the old data
                                if ( (ch + chNum)->background->varianceAccum <= *( (ch + chNum)->background->bestDeviations + \
                                    (ch + chNum)->background->bestIndex ) ) {
                                        (ch + chNum)->background->bestIndex = -1; // Denotes best is new value
                                }
                                // This condition means new value is worse than the worst. So don't shift unless we have to.
                                if ( (ch + chNum)->background->varianceAccum > *( (ch + chNum)->background->bestDeviations + \
                                    (ch + chNum)->background->worstIndex ) ) {
                                        (ch + chNum)->background->worstIndex = -1; //(ch + chNum)->background->baselinesHeld-1;
                                }
                            }
                            break;
			/*
                        case 2: // skew
                            if ( (ch + chNum)->background->baselinesHeld > 0 ) {
                                // This condition means new skew is lower (better) than the best in the old data
                                if ( (ch + chNum)->background->skewAccum <= *( (ch + chNum)->background->bestSkews + \
                                    (ch + chNum)->background->bestIndex ) ) {
                                        (ch + chNum)->background->bestIndex = -1; // Denotes best is new value
                                }
                                // This condition means new value is worse than the worst. So don't shift unless we have to.
                                if ( (ch + chNum)->background->skewAccum > *( (ch + chNum)->background->bestSkews + \
                                    (ch + chNum)->background->worstIndex ) ) {
                                        (ch + chNum)->background->worstIndex = -1; //(ch + chNum)->background->baselinesHeld-1;
                                }
                            }
                            break;
                        case 3: // kurt
                            if ( (ch + chNum)->background->baselinesHeld > 0 ) {
                                // This condition means new kurtosis is lower (better) than the best in the old data
                                if ( (ch + chNum)->background->kurtAccum <= *( (ch + chNum)->background->bestKurts + \
                                    (ch + chNum)->background->bestIndex ) ) {
                                        (ch + chNum)->background->bestIndex = -1; // Denotes best is new value
                                }
                                // This condition means new value is worse than the worst. So don't shift unless we have to.
                                if ( (ch + chNum)->background->kurtAccum > *( (ch + chNum)->background->bestKurts + \
                                    (ch + chNum)->background->worstIndex ) ) {
                                        (ch + chNum)->background->worstIndex = -1; //(ch + chNum)->background->baselinesHeld-1;
                                }
                            }
                            break;
                        */
                        default: // p2p*var
                            if ( (ch + chNum)->background->baselinesHeld > 0 ) {
                                // This condition means new variance is lower (better) than the best in the old data
                                if ( ( (ch + chNum)->background->max - (ch + chNum)->background->min ) * \
                                    ( ( ch + chNum )->background->varianceAccum )  <= *( (ch + chNum)->background->bestP2Ps + \
                                    (ch + chNum)->background->bestIndex ) * ( *((ch + chNum)->background->bestDeviations + \
                                    (ch + chNum)->background->bestIndex ) ) ) {
                                        (ch + chNum)->background->bestIndex = -1; // Denotes best is new value
                                }
                                // This condition means new value is worse than the worst. So don't shift unless we have to.
                                if ( ( (ch + chNum)->background->max - (ch + chNum)->background->min ) * \
                                    ( ( ch + chNum )->background->varianceAccum ) >  *( (ch + chNum)->background->bestP2Ps + \
                                    (ch + chNum)->background->worstIndex ) * ( *((ch + chNum)->background->bestDeviations + \
                                    (ch + chNum)->background->worstIndex ) ) ) {
                                        (ch + chNum)->background->worstIndex = -1; //(ch + chNum)->background->baselinesHeld-1;
                                }
                            }
                            break;
                    }


                    // This just makes sure that if not full, it will always shift.				
                    if ( (ch + chNum)->background->baselinesHeld < cfg.thresholds.baselinesToHold ) {
                        (ch + chNum)->background->worstIndex = cfg.thresholds.baselinesToHold - 1;
                    }


                    // Iterate starting from end. This will only shift if needed...
                    // 	If NO elements were in array, no shift will happen
                    // 	If NOT full, worstIndex should have been set to -1 (indicate shift all)
                    //	If FULL, worstIndex == -1 will mean don't shift, != -1 will mean shift from worst 
                    for (j = (ch + chNum)->background->baselinesHeld - 1; j>=0; j--) {
                        // Starting at end, ONLY shift right if iterator is less than worstIndex.
                        //	This is so the worst index is overwritten and the new stuff if added to front.
                        if ( j <= (ch + chNum)->background->worstIndex && \
                            (ch + chNum)->background->baselinesHeld == cfg.thresholds.baselinesToHold && j!=0 ) {
                                // This condition is to shift everything right based on (ch + chNum)->background->worstIndex.
                                *((ch + chNum)->background->bestDeviations+j) = *((ch + chNum)->background->bestDeviations+j-1);
                                *((ch + chNum)->background->bestBaselines+j) = *((ch + chNum)->background->bestBaselines+j-1);
                                *((ch + chNum)->background->bestTimes+j) = *((ch + chNum)->background->bestTimes+j-1);
                                *((ch + chNum)->background->bestP2Ps+j) = *((ch + chNum)->background->bestP2Ps+j-1);
                                //*((ch + chNum)->background->bestSkews+j) = *((ch + chNum)->background->bestSkews+j-1);
                                //*((ch + chNum)->background->bestKurts+j) = *((ch + chNum)->background->bestKurts+j-1);
                        }
                        if ( (ch + chNum)->background->baselinesHeld < cfg.thresholds.baselinesToHold ) {
                            *((ch + chNum)->background->bestDeviations+j+1) = *((ch + chNum)->background->bestDeviations+j);
                            *((ch + chNum)->background->bestBaselines+j+1) = *((ch + chNum)->background->bestBaselines+j);
                            *((ch + chNum)->background->bestTimes+j+1) = *((ch + chNum)->background->bestTimes+j);
                            *((ch + chNum)->background->bestP2Ps+j+1) = *((ch + chNum)->background->bestP2Ps+j);
                            //*((ch + chNum)->background->bestSkews+j+1) = *((ch + chNum)->background->bestSkews+j);
                            //*((ch + chNum)->background->bestKurts+j+1) = *((ch + chNum)->background->bestKurts+j);
                        }
                    }

                    // Only increment if array wasn't full. At this point, it should always have added if it could have.
                    if ( (ch + chNum)->background->baselinesHeld < cfg.thresholds.baselinesToHold ) {
                        (ch + chNum)->background->baselinesHeld++;
                    }
                    // We know that the shift occurred ONLY if array wasn't full and worstIndex != -1
                    // Now that everything is shifted away from first index, add new data to beginning
                    if( (ch + chNum)->background->worstIndex != -1 ) {	
                        *((ch + chNum)->background->bestDeviations) = (ch + chNum)->background->varianceAccum;
                        *((ch + chNum)->background->bestBaselines) = (ch + chNum)->background->baselineAccum;
                        *((ch + chNum)->background->bestTimes) = globalLoopCt;
                        *((ch + chNum)->background->bestP2Ps) = (ch + chNum)->background->max - (ch + chNum)->background->min;
                        //*((ch + chNum)->background->bestSkews) = (ch + chNum)->background->skewAccum;
                        //*((ch + chNum)->background->bestKurts) = (ch + chNum)->background->kurtAccum;
                    }
    				
                    // This means a shift happened with the bestIndex not moving 
                    //	because the worst was overwritten to the left (i.e. Do NOTHING)
                    if ( ( (ch + chNum)->background->baselinesHeld == cfg.thresholds.baselinesToHold ) && \
                        ( (ch + chNum)->background->bestIndex > (ch + chNum)->background->worstIndex ) ) {
                    }
                    else { 
                        (ch + chNum)->background->bestIndex += 1; 
                    }	
    
                    (ch + chNum)->background->baseline = *( (ch + chNum)->background->bestBaselines + (ch + chNum)->background->bestIndex );

		    if( *((ch + chNum)->background->bestDeviations + (ch + chNum)->background->bestIndex) > 4194304) {
		        *((ch + chNum)->background->bestDeviations + (ch + chNum)->background->bestIndex) = 4194304;
		        *((ch + chNum)->background->bestP2Ps + (ch + chNum)->background->bestIndex) = 65535;
                    }

		    (ch + chNum)->background->std = SQRTTBL[*((ch + chNum)->background->bestDeviations + (ch + chNum)->background->bestIndex)];
                    (ch + chNum)->background->p2p = *((ch + chNum)->background->bestP2Ps + (ch + chNum)->background->bestIndex);
                    //(ch + chNum)->background->skew = *((ch + chNum)->background->bestSkews + (ch + chNum)->background->bestIndex);
                    //(ch + chNum)->background->kurt = *((ch + chNum)->background->bestKurts + (ch + chNum)->background->bestIndex);
                    (ch + chNum)->background->time = *((ch + chNum)->background->bestTimes + (ch + chNum)->background->bestIndex);
    
                    zeroIntervalFlag = 0; // Must set this here to ensure it begins accumulating again
                        // at the next if statement.
                }
            }
			
            // Third check for when on appropriate division and to begin accumulating       
            if ( onDivision && !zeroIntervalFlag ) {//(ch + chNum)->background->varianceAccum == 0 ){
                // Single line absolute value pull into accumulator
                for ( chNum = 1; chNum >= 0; chNum-- ) {
                    tmpGausVar = \
                        ((*((ch + chNum)->lpfptr))*(*((ch + chNum)->lpfptr))) + \
                        ((*((ch + chNum)->ptr))*(*((ch + chNum)->ptr))) - \
                        (((*((ch + chNum)->lpfptr))*(*((ch + chNum)->ptr)))<<1);
                    
                    // Now store variance to variance accumulator
                    (ch + chNum)->background->varianceAccum = tmpGausVar;
                    
                    // Skew is + (meas-act)^3 = (meas
                    //(ch + chNum)->background->skewAccum = \
                        tmpGausVar * ( (int)(*(ch + chNum)->ptr) - (int)(*(ch+chNum)->lpfptr) );
                    //    ((*((ch + chNum)->ptr))*(*((ch + chNum)->ptr))*(*((ch + chNum)->ptr))) - \
                    //    ((*((ch + chNum)->lpfptr))*(*((ch + chNum)->lpfptr))*(*((ch + chNum)->lpfptr))) - \
                    //    (3*(*((ch + chNum)->ptr))*(*((ch + chNum)->ptr))*(*((ch + chNum)->lpfptr))) + \
                    //    (3*(*((ch + chNum)->ptr))*(*((ch + chNum)->lpfptr))*(*((ch + chNum)->lpfptr)));

                    // Kurtosis is var^2
                    //(ch + chNum)->background->kurtAccum = tmpGausVar*tmpGausVar;

                    // Just add, will divide down later
                    (ch + chNum)->background->baselineAccum = *((ch + chNum)->ptr); 
                    (ch + chNum)->background->max = *((ch + chNum)->ptr);//LPFptr;
                    (ch + chNum)->background->min = *((ch + chNum)->ptr);//LPFptr;
    
                    zeroIntervalFlag = 1; // Must set this here to allow accumulation to continue
                }
            }
			   
            // Final check to see if we have reached end of buffer....
            if ( ch[0].ptr >= oversamp_sz + ch[0].buf - 1 ) {
                //for( chNum = 0; chNum < 2; chNum++ ) {
                for ( chNum = 1; chNum >= 0; chNum-- ) {
                    //printf("End of buffer null, should only run once per buffer\n");
                    (ch + chNum)->background->baselineAccum = 0;//-1;
                    (ch + chNum)->background->varianceAccum = 0;//-1;
                    (ch + chNum)->background->max = 0;
                    (ch + chNum)->background->min = 0;
                    (ch + chNum)->background->skewAccum = 0;//4194304;
                    (ch + chNum)->background->kurtAccum = 0;//4194304;
    
                    zeroIntervalFlag = 0;
                }
            }

	
            //////////////////////////////////////////////////////////////////////////////////
            /*				END BASELINE CODE				*/
            //////////////////////////////////////////////////////////////////////////////////


            // Basically if baseline has not been asserted OR on a waiting interval, we cannot analyze sooooo
            //	BE CAREFUL, may need to separate out this continue statement on a per channel basis
            // Stop index hold iteration only once reached index.
            ch[0].indexToWaitUntil = 0;
            ch[1].indexToWaitUntil = 0;
	
            //////////////////////////////////////////////////////////////////////////
            /*			BEGIN PARTICLE FIND				*/
            //////////////////////////////////////////////////////////////////////////			
						
            for ( chNum = 1; chNum >= 0; chNum-- ) {
                // If baseline exists AND not in waiting, then can do something...
                if ( globalLoopCt >= 2000000 && (ch + chNum)->enable ) {//!(ch + chNum)->indexToWaitUntil ) {
                    //MUST come up with condition to carryover data from previous buffer if
                    //	stuff is on edge....
    
                    // Routine for searching for the beginning of a particle->...
                    //	Searches for consecutive times that LPF exceeds baseline with acceptable number of erroneous drops
                    if ( !(ch + chNum)->startFound ) {	
                        //printf("Start Check routine running\n");			
                        if ( (ch + chNum)->startCnt == cfg.thresholds.minStartPts ) {
                            //printf("Start Found\n");
                            // Successful start condition..
                            (ch + chNum)->startFound = 1;               //(ch + chNum)->startIndex = (ch + chNum)->lpfptr-1;
                            (ch + chNum)->startIndex = (ch + chNum)->lpfptr - \
                                (ch + chNum)->startDropCtr - \
                                cfg.thresholds.minStartPts; // Setting it to the ptr of LPF.
                            (ch + chNum)->startDropCtr = 0;
                            (ch + chNum)->startCnt = 0;
                            clock_gettime(CLOCK_MONOTONIC, &((ch + chNum)->startTime));
                        }
                    }
                    if ( !(ch + chNum)->startFound ) {
                        if ( *((ch + chNum)->lpfptr) > (ch + chNum)->background->baseline + \
                            ((ch + chNum)->background->std * cfg.thresholds.sigmaThreshold ) ) {
                                (ch + chNum)->startCnt++;
                        }
                        else {
                            if ( (ch + chNum)->startDropCtr != cfg.thresholds.maxStartDrops ) {
                                (ch + chNum)->startDropCtr += 1;
                            }
                            else {
                                // This means a fail condition occured....
                                (ch + chNum)->startDropCtr = 0;
                                (ch + chNum)->startCnt = 0;
                                (ch + chNum)->statSigCnt = 0;
    
                                // Revert particle metrics back to current value
                                (ch + chNum)->particle->rHM = \
                                    (ch + chNum)->particle->r3QM = \
                                    (ch + chNum)->particle->lHM = \
                                    (ch + chNum)->particle->l3QM = \
                                    (ch + chNum)->particle->lMin = \
                                    (ch + chNum)->particle->rMin = \
                                    (ch + chNum)->particle->peak = \
                                    (ch + chNum)->lpfptr; 
                                (ch + chNum)->particle->peakAccum = *((ch + chNum)->particle->peak);
                                (ch + chNum)->particle->peakWidth = 1;
                                (ch + chNum)->particle->HMThresh = \
                                    ( ( *((ch + chNum)->particle->peak) - \
                                    (ch + chNum)->background->baseline ) >> 1 ) + \
                                    (ch + chNum)->background->baseline;
                                (ch + chNum)->particle->TQMThresh = \
                                    ( ( ( *((ch + chNum)->particle->peak) - \
                                    (ch + chNum)->background->baseline ) * 3 ) >> 2 ) + \
                                    (ch + chNum)->background->baseline;
                            }
                        }
                    }
    
                    // Continually check for peak height, left min, right min, peakWidth
                    // TRUST that it will always be reset whenever it actually needs to be
                    //	Under start condition fail OR after particle analysis..
                    if ( *((ch + chNum)->lpfptr) > *((ch + chNum)->particle->peak) ) {
                        // New peak is found!
                        (ch + chNum)->particle->rHM = \
                            (ch + chNum)->particle->r3QM = \
                            (ch + chNum)->particle->lHM = \
                            (ch + chNum)->particle->l3QM = \
                            (ch + chNum)->particle->lMin = \
                            (ch + chNum)->particle->rMin = \
                            (ch + chNum)->particle->peak = \
                            (ch + chNum)->lpfptr; 
                        (ch + chNum)->particle->peakAccum = *((ch + chNum)->particle->peak);
                        (ch + chNum)->particle->peakWidth = 1; 
                        (ch + chNum)->particle->HMThresh = \
                            ( ( *((ch + chNum)->particle->peak) - \
                            (ch + chNum)->background->baseline ) >> 1 ) + \
                            (ch + chNum)->background->baseline;
                        (ch + chNum)->particle->TQMThresh = \
                            ( ( ( *((ch + chNum)->particle->peak) - \
                            (ch + chNum)->background->baseline ) * 3 ) >> 2 ) + \
                            (ch + chNum)->background->baseline;
                    }
    				
                    // This is accumulator for peak values that are within 1P2P of peak
                    if ( *((ch + chNum)->particle->peak) - \
                        ( (ch + chNum)->background->std * cfg.thresholds.sigmaThreshold ) < \
                        *((ch + chNum)->lpfptr) ) {
                            (ch + chNum)->particle->peakAccum += *((ch + chNum)->lpfptr);
                            (ch + chNum)->particle->peakWidth += 1;
                    }
    				
                    // IF new value is less than held right minima, overwrite right minima	
                    if ( *((ch + chNum)->lpfptr) < *((ch + chNum)->particle->rMin) ){
                        (ch + chNum)->particle->rMin = (ch + chNum)->lpfptr;
                    }
    				
                    // This is the search for the right HWHM and right HW3QM				
                    // Set to ONLY update when first cross is found 
                    //     (using ptr compare (ch + chNum)->particle->rHM <= (ch + chNum)->particle->peak)
                    if ( (*((ch + chNum)->lpfptr) <= (ch + chNum)->particle->HMThresh) && \
                        ((ch + chNum)->lpfptr != (ch + chNum)->lpf) && \
                        (*((ch + chNum)->lpfptr - 1) >= (ch + chNum)->particle->HMThresh) && \
                        ((ch + chNum)->particle->rHM <= (ch + chNum)->particle->peak) ) {
                            (ch + chNum)->particle->rHM = (ch + chNum)->lpfptr;	
                    }
                    if ( (*((ch + chNum)->lpfptr) <= (ch + chNum)->particle->TQMThresh) && \
                        ((ch + chNum)->lpfptr != (ch + chNum)->lpf) && \
                        (*((ch + chNum)->lpfptr - 1) >= (ch + chNum)->particle->TQMThresh) && \
                        ((ch + chNum)->particle->r3QM <= (ch + chNum)->particle->peak) ) {
                            (ch + chNum)->particle->r3QM = (ch + chNum)->lpfptr;
                    } 
    		
                    // If new value is greater than 1P2P off right minima, terminate particle->
                    //	But only if particle start has been found already
                    // TRUST that this will never flag an end when still searching for peak
                    //	May be a problem if rightMin falls slightly off peak exceeds 1P2P
                    if ( (*((ch + chNum)->lpfptr) > *((ch + chNum)->particle->rMin) + \
                        ( (ch + chNum)->background->std * cfg.thresholds.sigmaThreshold ) ) && (ch + chNum)->startFound ) {
                            (ch + chNum)->startCnt = 0;//minStartPts;
                            (ch + chNum)->backToBaselineCnt = 0;//backToBaselinePts;
                            (ch + chNum)->startDropCtr = 0;				
    	
                            //Denote end found	
                            (ch + chNum)->endFound = 1;
                            // Denote end at last time right minima was identified
                            (ch + chNum)->endIndex = (ch + chNum)->particle->rMin;
                            // Used to indicate that a particle convolution flagged...
                            //printf("Convolution flag\n");
                            (ch + chNum)->particle->convFlag = 1;
                    }
    
                    // This should not run run if a convolution end was found!!	
                    if ( (ch + chNum)->startFound && !(ch + chNum)->endFound ) {
                        //printf("End Found\n");
                        if ( (ch + chNum)->backToBaselineCnt == cfg.thresholds.backToBaselinePts ) {
                            // Successful end find
                            //printf("End Found\n");
                            (ch + chNum)->endIndex = (ch + chNum)->lpfptr;//i;
                            (ch + chNum)->endFound = 1;
                            (ch + chNum)->backToBaselineCnt = 0;
                            clock_gettime(CLOCK_MONOTONIC, &((ch + chNum)->endTime) );
                        }

                        if ( !(ch + chNum)->endFound && ( *((ch + chNum)->lpfptr) <  \
                            (ch + chNum)->background->baseline + \
                            ( (ch + chNum)->background->std * \
                            cfg.thresholds.sigmaThreshold) ) ) {
                                (ch + chNum)->backToBaselineCnt++;
                        }
                    }
    		
                    // For carrying statistically significant information into particle routine...
                    //	Should run every loop, resets only if it fails out start or end finds.
                    // 	Quick statistical cnt of when LPF > baseline + 1sigma;
    				
                    //Uncomment to possibly reduce computation if sqrt too intensive
                    // if ( (ch + chNum)->startFound  || ( (ch + chNum)->startCnt > 2 ) ) 
                    
                    // May also consider comparing (LPF - baseline)^2 > variance instead of (LPF - Baseline) > sqrt(variance)
                    if ( *((ch + chNum)->lpfptr) > (ch + chNum)->background->baseline + (ch + chNum)->background->std ) {
                        // This means point of LPF that exceeds statistical noise.
                        (ch + chNum)->statSigCnt++;
                    }
    			
                    if ( (ch + chNum)->startFound && (ch + chNum)->endFound ) {
                        // Now analyze particle->..
                        // Verify how much of the data lies below the peak corresponding to the best p2p
                        //   This appears to work well for rejecting false positives
    
                        //printf("Particle Found\n");
    
                        // Note: Written this way is fixed point arithmetic. So if 2 points in a 3 point window.
                        //	result will be 2*100/3 = 66
                        // ATTENTION: I think == -1 means will never flag a particle as bad?
                        if ( ((ch + chNum)->endIndex > (ch + chNum)->startIndex ) && \
                            ((ch + chNum)->statSigCnt*100)/((ch + chNum)->endIndex - \
                            (ch + chNum)->startIndex) == -1 ) {//< 50 ) {
                                // Statistically insignificant, so particle is bad. Null everything back.
                                (ch + chNum)->statSigCnt = 0;
                                (ch + chNum)->startFound = 0;
                                (ch + chNum)->endFound = 0;
                        }
                        else { // Successful find? 
                            // Save particle->....
                            // By this point, *peak, *rHM, *r3QM, pWidth, and pAccum have been found.
                            // Now just scan backwards to expand the peak and find the l3QM and lHM
  
                            // Save appropriate particle params
                            if ( cfg.files.file[parsIndex].enable ) {
                                fprintf(cfg.files.file[parsIndex].fptr, "%lu, %lu, %llu, %u, %u, %u, %u, %u, %u, %u, %u, %u, %u, %u\n",\
                                    (unsigned long int)(ch + chNum)->startTime.tv_sec, \
                                    (unsigned long int)(ch + chNum)->startTime.tv_nsec, \
                                    (unsigned long long int)globalLoopCt, \
                                    (unsigned int)(ch + chNum)->background->baseline, \
                                    (unsigned short int)(ch + chNum)->background->std, \
                                    (unsigned int)(ch + chNum)->background->p2p, \
                                    (unsigned int)(*((ch + chNum)->startIndex)), \
                                    (unsigned int)((ch + chNum)->particle->peak - (ch + chNum)->particle->lHM), \
                                    (unsigned int)((ch + chNum)->particle->peak - (ch + chNum)->particle->l3QM), \
                                    (unsigned int)(*((ch + chNum)->particle->peak)), \
                                    (unsigned int)((ch + chNum)->particle->r3QM - (ch + chNum)->particle->peak), \
                                    (unsigned int)((ch + chNum)->particle->rHM - (ch + chNum)->particle->peak), \
                                    (unsigned int)(*((ch + chNum)->endIndex)), \
                                    (unsigned int)((ch + chNum)->particle->convFlag) );
                            }		
                            /*
                            //Diagnostic to save particle that has a convolution flag set
                            if ( (ch + chNum)->particle->convFlag ) {
                            	fprintf(particleConvFilePtr, "%lu,%lu", \
                            		(unsigned long int)(ch + chNum)->startTime.tv_sec, \
                            		(unsigned long int)(ch + chNum)->startTime.tv_nsec );
                            	for ( (ch + chNum)->startIndex = (ch + chNum)->startIndex; \
                                    (ch + chNum)->startIndex < (ch + chNum)->endIndex; \
                                    (ch + chNum)->startIndex++ ) {
                                        fprintf(particleConvFilePtr, ",%u", \
                                            (unsigned int)(*((ch + chNum)->startIndex));
                            	}
                            	fprintf(particleConvFilePtr, "\n");
                            }
                            */
   
                            /* 
                            tmpx = (double)(*((ch + chNum)->particle->peak) - \
                                (ch + chNum)->background->baseline);
                            tmpx = log10(tmpx*7.0);
                            tmpx2 = 0.00;
                            for( j = 0; j<MIEPOLYORDER; j++ ) {
                                tmpx2 += mieCoef[j]*pow(tmpx,j);
                            }
                            */
                            //printf("%u\n",MIE[*(ch[0]->particle->peak)-ch[0]->background->baseline]);
                           
                            if ( *((ch + chNum)->particle->peak) > ((ch + chNum)->background->baseline ) ) { 
                                (ch + chNum)->particle->size = \
                                    *((ch + chNum)->particle->peak) - \
                                    (ch + chNum)->background->baseline;
                            }
                            else {
                                // Assert to zero to demonstrate negative particle
                                (ch + chNum)->particle->size = 0;
                            }

                            (ch + chNum)->particle->size = (ch + chNum)->particle->size <= 65535 ? \
                                (ch + chNum)->particle->size : 65535;
    	
                            for (j=0; j<NUMBINS; j++) {
                                if ( (ch + chNum)->particle->size >= (ch + chNum)->histogram->histBinEdges[j] && \
                                    (ch + chNum)->particle->size < (ch + chNum)->histogram->histBinEdges[j+1] ) {
                                        (ch + chNum)->histogram->histCnts[j]++;
                                        break;
                                }							
                            }
    
                            if ( (ch + chNum)->particle->convHist && (ch + chNum)->particle->convFlag ) {
                                (ch + chNum)->particle->convHist = 0;	
                            }

                            // Reset all particle params....
    
                            // IF convolution flag was set, we know to just place left index at where end was
                            // Null everything else?
                            if ( (ch + chNum)->particle->convFlag ) {
                                (ch + chNum)->particle->lMin = \
                                    (ch + chNum)->startIndex = \
                                    (ch + chNum)->particle->rMin;
                                (ch + chNum)->startFound = 1;
                                (ch + chNum)->particle->rHM = \
                                    (ch + chNum)->particle->r3QM = \
                                    (ch + chNum)->particle->lHM = \
                                    (ch + chNum)->particle->l3QM = \
                                    (ch + chNum)->particle->peak = \
                                    (ch + chNum)->particle->rMin = \
                                    (ch + chNum)->lpfptr; 
    							
                                // Assert this to ensure next particle is also flagged
                                (ch + chNum)->particle->convHist = 1;
                            }
                            else {
                                // If convolution flag was not set, can null everything back to current index	
                                (ch + chNum)->particle->rHM = \
                                    (ch + chNum)->particle->r3QM = \
                                    (ch + chNum)->particle->lHM = \
                                    (ch + chNum)->particle->l3QM = \
                                    (ch + chNum)->particle->lMin = \
                                    (ch + chNum)->particle->rMin = \
                                    (ch + chNum)->particle->peak = \
                                    (ch + chNum)->lpfptr; 
                                (ch + chNum)->startFound = 0;
                            }
    				
                            (ch + chNum)->endFound = 0;
    	 					
                            (ch + chNum)->particle->peakAccum = *((ch + chNum)->particle->peak);
                            (ch + chNum)->particle->peakWidth = 1; 
                            (ch + chNum)->particle->HMThresh = \
                                ( ( *((ch + chNum)->particle->peak) - \
                                (ch + chNum)->background->baseline ) >> 1 ) + \
                                (ch + chNum)->background->baseline;
                            (ch + chNum)->particle->TQMThresh = \
                                ( ( ( *((ch + chNum)->particle->peak) - \
                                (ch + chNum)->background->baseline ) * 3 ) >> 2 ) + \
                                (ch + chNum)->background->baseline;
    						
                            // Always renull convolution flag after particle is analyzed
                            (ch + chNum)->particle->convFlag = 0;

                            // ROUTINE FOR SAVING ENTIRE PARTICLES
                            if ( cfg.files.file[rawIndex].enable ) {
                                fprintf( cfg.files.file[rawIndex].fptr, "%d", chNum);
                                for ( (ch + chNum)->startIndex = (ch + chNum)->startIndex, \
                                    (ch + chNum)->startIndex, (ch + chNum)->particle->lMin = \
                                    (ch + chNum)->startIndex, (ch + chNum)->particle->peak = \
                                    (ch + chNum)->startIndex; (ch + chNum)->startIndex < \
                                    (ch + chNum)->endIndex; (ch + chNum)->startIndex++ ) {
                                        fprintf(  cfg.files.file[rawIndex].fptr , ", %d", \
                                            *((ch+ chNum)->startIndex) );
                                }
                                fprintf( cfg.files.file[rawIndex].fptr, "\n");
                            }

                            // ROUTINE FOR SAVING PEAK HEIGHTS
                            if ( cfg.files.file[peakIndex].enable ) {
                                fprintf(cfg.files.file[peakIndex].fptr, "%d, %u, %u\n", chNum, \
                                    (ch+chNum)->background->baseline, *((ch+chNum)->particle->peak));
                            }
    	
                            /*
                            if ( cfg.files.file[rawIndex].enable ) {	
                                for ( (ch + chNum)->startIndex = (ch + chNum)->startIndex; \
                                    (ch + chNum)->startIndex < (ch + chNum)->endIndex; \
                                    (ch + chNum)->startIndex++ ) {
                                        fprintf( cfg.files.file[rawIndex].fptr, ", %d", *((ch + chNum)->startIndex));
                                }
                                fprintf( cfg.files.file[rawIndex].fptr, "\n");
                            }						
                            */

                            // Claim successful find.
                            (ch + chNum)->particleCnt++;
    				
                            // Now tell how long to wait...
                            (ch + chNum)->indexToWaitUntil = globalLoopCt + 1;// + 10;	
                        }					
                    }
    
                } // End of if statement that determines whether to enter particle find routine.
			
                if ( (ch + chNum)->ptr >= oversamp_sz + (ch + chNum)->buf - 1 || (ch + chNum)->ptr == (ch + chNum)->buf ) {
                    (ch + chNum)->startFound = 0;
                    (ch + chNum)->endFound = 0;
                    (ch + chNum)->startCnt = 0;
                    (ch + chNum)->startDropCtr = 0;
                    (ch + chNum)->backToBaselineCnt = 0;
                    (ch + chNum)->particle->rHM = \
                        (ch + chNum)->particle->r3QM = \
                        (ch + chNum)->particle->lHM = \
                        (ch + chNum)->particle->l3QM = \
                        (ch + chNum)->particle->lMin = \
                        (ch + chNum)->particle->rMin = \
                        (ch + chNum)->particle->peak = \
                        (ch + chNum)->lpf; // Setting this back to beginning of buffer 
                    (ch + chNum)->particle->peakAccum = \
                        *((ch + chNum)->particle->peak);
                    (ch + chNum)->particle->peakWidth = 1;
                    (ch + chNum)->particle->HMThresh = \
                        ( ( *((ch + chNum)->particle->peak) - \
                        (ch + chNum)->background->baseline ) >> 1 ) + \
                        (ch + chNum)->background->baseline;
                    (ch + chNum)->particle->TQMThresh = \
                        ( ( ( *((ch + chNum)->particle->peak ) - \
                        (ch + chNum)->background->baseline ) * 3 ) >> 2 ) + \
                        (ch + chNum)->background->baseline;
                }

            } // End of channel number for loop


        } // End of buffer loop 
        clock_gettime(CLOCK_MONOTONIC, &compt2);
	
        chNum = 0;	
        if ( cfg.files.file[diagIndex].enable ) {
            switch ( cfg.files.diagnosticSaveOption ) {
                case 0: // This is a full buffer save....
                    for ( ch[0].ptr = (ch + chNum)->buf, ch[1].ptr = ch[1].buf;\
                        (ch + chNum)->ptr<oversamp_sz+(ch + chNum)->buf;\
                        (ch + chNum)->ptr++, ch[1].ptr++ )
                            fprintf(cfg.files.file[diagIndex].fptr,"%d, %d\n",\ 
                                *((ch + chNum)->ptr),*(ch[1].ptr) );
                    break;
                case 1: // This is full ch1 buffer save (no channel 2.  
                    for ( (ch + chNum)->ptr = (ch + chNum)->buf, \
                        ch[1].ptr = ch[1].buf; (ch + chNum)->ptr<oversamp_sz+\
                        (ch + chNum)->buf; (ch + chNum)->ptr++, ch[1].ptr++ )
                            fprintf(cfg.files.file[diagIndex].fptr,"%d, %d\n",\
                                *((ch + chNum)->ptr) ,*(ch[1].ptr) );
                    break;
                case 2: // This is full ch2 buffer save (no channel 2.  
                    for( (ch + chNum)->ptr = (ch + chNum)->buf, ch[1].ptr = \
                        ch[1].buf; (ch + chNum)->ptr<oversamp_sz+\
                        (ch + chNum)->buf; (ch + chNum)->ptr++, ch[1].ptr++ )
                            fprintf(cfg.files.file[diagIndex].fptr,"%d, %d\n",\
                                *((ch + chNum)->ptr) ,*(ch[1].ptr) );
                    break;
                case 3: // This is full ch1 and ch2 LPF saves...
                    for ( (ch + chNum)->lpfptr = (ch + chNum)->lpf, \
                        ch[1].lpfptr = ch[1].lpf; \
                        (ch + chNum)->lpfptr<oversamp_sz+(ch + chNum)->lpf; \
                        (ch + chNum)->lpfptr++, ch[1].lpfptr++ )
                            fprintf(cfg.files.file[diagIndex].fptr,"%d, %d\n",\
                                *((ch + chNum)->lpfptr) ,*(ch[1].lpfptr) );
                    break;
                case 4: // This is full ch1 LPF save (no channel 2).  
                    for ( (ch + chNum)->lpfptr = (ch + chNum)->lpf;\
                        (ch + chNum)->lpfptr<oversamp_sz+(ch + chNum)->lpf;\
                        (ch + chNum)->lpfptr++ )
                            fprintf(cfg.files.file[diagIndex].fptr,"%d\n",\
                                *((ch + chNum)->lpfptr) );		
                    break;
                case 5: // This is full ch2 LPF save (no channel 1.  
                    for ( ch[1].lpfptr = ch[1].lpf; \
                        ch[1].lpfptr<oversamp_sz+(ch + chNum)->lpf;\
                        ch[1].lpfptr++ )
                            fprintf(cfg.files.file[diagIndex].fptr,"%d\n",\
                                *(ch[1].lpfptr) );		
                    break;
                case 6: // This is for a first AND last n points of buffer of ch1 and ch2....
                    fprintf(cfg.files.file[diagIndex].fptr,"-2\n");
                    for ( (ch + chNum)->ptr = (ch + chNum)->buf, \
                        ch[1].ptr = ch[1].buf; \
                        (ch + chNum)->ptr<(ch + chNum)->buf + 1024; \
                        (ch + chNum)->ptr++, ch[1].ptr++ )
                            fprintf(cfg.files.file[diagIndex].fptr,"%u, %u\n", \
                                *((ch + chNum)->ptr) ,*(ch[1].ptr) );		
                    fprintf(cfg.files.file[diagIndex].fptr,"-1\n"); 
                    for ( (ch + chNum)->ptr=(ch + chNum)->buf+oversamp_sz-1024,\
                        ch[1].ptr=ch[1].buf+oversamp_sz-1024; \
                        (ch + chNum)->ptr<oversamp_sz+(ch + chNum)->buf;\
                        (ch + chNum)->ptr++,ch[1].ptr++)
                            fprintf(cfg.files.file[diagIndex].fptr, "%u, %u\n",\
                                *((ch + chNum)->ptr), *(ch[1].ptr) );
                    break;
                case 7: // This is for an every nth points buffer save
                    fprintf(cfg.files.file[diagIndex].fptr,"-2\n");
                    for ( (ch + chNum)->ptr = (ch + chNum)->buf, \
                        ch[1].ptr = ch[1].buf; (ch + chNum)->ptr<oversamp_sz+\
                        (ch + chNum)->buf; (ch + chNum)->ptr+=128,\
                        ch[1].ptr+=128 )
                            fprintf(cfg.files.file[diagIndex].fptr,"%d, %d\n",\
                                *((ch + chNum)->ptr),*(ch[1].ptr));
                    break;
                case 8: // This is for a first AND last n points of LPF of ch1 and ch2....
                    fprintf(cfg.files.file[diagIndex].fptr,"-2\n");
                    for ( (ch + chNum)->lpfptr = (ch + chNum)->lpf, \
                        ch[1].lpfptr = ch[1].lpf; \
                        (ch + chNum)->lpfptr<(ch + chNum)->lpf + 1024; \
                        (ch + chNum)->lpfptr++, ch[1].lpfptr++ )
                            fprintf(cfg.files.file[diagIndex].fptr,"%d, %d\n",\
                                *((ch + chNum)->lpfptr) ,*(ch[1].lpfptr) );		
                    fprintf(cfg.files.file[diagIndex].fptr,"-1\n"); 
                    for ( (ch + chNum)->lpfptr=(ch + chNum)->lpf+\
                        oversamp_sz-1024, ch[1].lpfptr=ch[1].lpf+\
                        oversamp_sz-1024; (ch + chNum)->lpfptr<oversamp_sz+\
                        (ch + chNum)->lpf; \
                        (ch + chNum)->lpfptr++,ch[1].lpfptr++)
                            fprintf(cfg.files.file[diagIndex].fptr, "%d, %d\n",\
                                *((ch + chNum)->lpfptr) , *(ch[1].lpfptr) );
                    break;
                case 9: // This is for an every nth points buffer save
                    fprintf(cfg.files.file[diagIndex].fptr,"-2\n");
                    for ( (ch + chNum)->ptr = (ch + chNum)->buf, ch[1].ptr = \
                        ch[1].buf; (ch + chNum)->ptr<oversamp_sz+\
                        (ch + chNum)->buf; (ch + chNum)->ptr+=128, \
                        ch[1].ptr+=128 )
                            fprintf(cfg.files.file[diagIndex].fptr,"%d, %d\n",\
                                *((ch + chNum)->ptr) ,*(ch[1].ptr));
                    break;
                case 10: // This is full buffer save comparing ch1 to ch1 LPF....
                    for ( (ch + chNum)->ptr = (ch + chNum)->buf, \
                        (ch + chNum)->lpfptr = (ch + chNum)->lpf; \
                        (ch + chNum)->ptr<oversamp_sz+(ch + chNum)->buf;\
                        (ch + chNum)->ptr++, (ch + chNum)->lpfptr++ )
                            fprintf(cfg.files.file[diagIndex].fptr,"%d, %d\n",\
                                *((ch + chNum)->ptr) ,*((ch + chNum)->lpfptr) );
                    break;
                case 11: // This is for a first AND last n points of buffer of ch1 and (ch + chNum)->lpfBuffer....
                    fprintf(cfg.files.file[diagIndex].fptr,"-2\n"); 
                    for ( (ch + chNum)->ptr = (ch + chNum)->buf, \
                        (ch + chNum)->lpfptr = (ch + chNum)->lpf; \
                        (ch + chNum)->ptr<(ch + chNum)->buf + 1024; \
                        (ch + chNum)->ptr++, (ch + chNum)->lpfptr++ )
                            fprintf(cfg.files.file[diagIndex].fptr,"%u, %u\n",\
                                *((ch + chNum)->ptr) ,*((ch + chNum)->lpfptr) );		
                    fprintf(cfg.files.file[diagIndex].fptr,"-1\n"); 
                    for ( (ch + chNum)->ptr=(ch + chNum)->buf+oversamp_sz-1024,\
                        (ch + chNum)->lpfptr=(ch + chNum)->lpf+oversamp_sz-1024;\
                        (ch + chNum)->ptr<oversamp_sz+(ch + chNum)->buf;\
                        (ch + chNum)->ptr++,(ch + chNum)->lpfptr++)
                            fprintf(cfg.files.file[diagIndex].fptr, "%u, %u\n",\
                                *((ch + chNum)->ptr) , *((ch + chNum)->lpfptr) );
                    break;
                case 12: // This is full buffer save of ch1 and ch2 with LPFs....
                    for ( ch[0].ptr = ch[0].buf, ch[0].lpfptr = ch[0].lpf,\
                        ch[1].ptr = ch[1].buf, ch[1].lpfptr = ch[1].lpf; \
                        ch[0].ptr<oversamp_sz+ch[0].buf; ch[0].ptr++, \
                        ch[0].lpfptr++, ch[1].ptr++, ch[1].lpfptr++ )
                            fprintf(cfg.files.file[diagIndex].fptr,\
                                "%u, %u, %u, %u\n", *(ch[0].ptr) ,\
                                *(ch[0].lpfptr), *(ch[1].ptr), \
                                *(ch[1].lpfptr) );
                    break;

            } // End of switch.

        } // End of if statement for if saving raw data


        printf("\e[1;1H\e[2J");

        printf("Global Loop Ctr: %llu\n", globalLoopCt);
        // Buffer number should be cyclical from 0 to (bufferChunks - 1)
				
        clock_gettime(CLOCK_MONOTONIC, &bufwaitt1);	
        bufferAlternator = waitForNextBuffer();
        clock_gettime(CLOCK_MONOTONIC, &bufwaitt2);	

        // Seems to cause hold on process.	
        //printf("Last error: %d\n", beaglelogic_getlasterror());

        clock_gettime(CLOCK_MONOTONIC, &t2);	
  
        //printf("Waiting time for next buffer: %jd us\n", timediff(&bufwaitt1,&bufwaitt2));
        //printf("Time between buf calls %jd us\t Waiting time for next buffer: %jd us\n", timediff(&t1, &t2), timediff(&bufwaitt1,&bufwaitt2));
        //printf("Buffers Read: %lu\t Last Buffer Index Read: %u\n", buffersRead, bufferAlternator);
        //printf("Buffer read time: %jd us\t Computation Time: %jd us\n", timediff(&readt1,&readt2), timediff(&compt1,&compt2));
        //printf("Computation time: %jd us\n", timediff(&compt1,&compt2));
		
        if ( ( bufferAlternator != ( lastBufferRead + 1 ) ) && ( ( bufferAlternator + bufferBlocks - 1 ) != lastBufferRead ) ) {
            if ( bufferAlternator > lastBufferRead ) { 
                printf("%u", bufferAlternator - lastBufferRead - 1 ); 
                (ch)->buffersDropped = bufferAlternator - lastBufferRead - 1;
                (ch+1)->buffersDropped = bufferAlternator - lastBufferRead - 1;
            }
            else {
                printf("%u", bufferBlocks - lastBufferRead + bufferAlternator - 1);
                (ch)->buffersDropped = bufferBlocks + bufferAlternator - lastBufferRead - 1;
                (ch+1)->buffersDropped = bufferBlocks + bufferAlternator - lastBufferRead - 1;
            }
            printf(" BUFFERS WERE DROPPED\n");
            printf("Time between buf calls %jd us\t Waiting time for next buffer: %jd us\n", timediff(&t1, &t2), timediff(&bufwaitt1,&bufwaitt2));
            printf("Buffers Read: %lu\t Last Buffer Index Read: %u\n", buffersRead, bufferAlternator);
            printf("Buffer read time: %jd us\t Computation Time: %jd us\n", timediff(&readt1,&readt2), timediff(&compt1,&compt2));
        }
        lastBufferRead = bufferAlternator;

        // Histogram analysis and plotting
        //for(i=0; i<NUMBINS; i++) printf("%u,",histCnts[i]);
        //for(i=0; i<NUMBINS; i++) printf("%f,",histBinEdges[i]);

        //histMax = 0;
        //for(i=0;i<NUMBINS;i++) {
        //	if( histCnts[i] > histMax ) histMax = histCnts[i];
        //}

        /*	
		
        // Now that histMax is known, we divide into a new histogram in pixel space
        for ( i = PIXMAX; i>0; i-- ) {
            //first print cnt value 
            switch(i) {
                case PIXMAX: 
                    printf("%u\t", histMax);
                    break;
                case 1: 
                    printf("%u\t", 0);
                    break;
                default: 
                    printf("\t");
                    break;
            }
            printf("|");

            // Now iterate through to add "x" characters in bars where histCnt * PIXMAX / histMax < PIXMAX
            for ( j = 0; j<NUMBINS; j++ ) {
                if ( histMax > 0 && histCnts[j] * ((unsigned int)PIXMAX) / histMax > i ) {
                    printf("x");		
                }
                else {
                    printf(" ");
                }
                printf("\n");
            }
            //Print bottom line
            printf("\t");
            for ( i = 0; i<NUMBINS; i++ ) printf("_");
            printf("\n");
            //printf("\t%.2f", histBinEdges[0]);
            //printf("\n");
            //for( i = 0; i<NUMBINS-1; i++ ) printf("x");

            printf("\t");
            for (i = 0; i<NUMBINS-1; i++ ) {
                if ( i%10 == 0) {
                    printf("%5.1f     ", histBinEdges[i]);
                }
            }
            printf("\n\t");
            for (i = 0; i<NUMBINS-1; i++ ) {
                if ( (i+5)%10 == 0) {
                    printf("     %5.1f", histBinEdges[i]);
                }
            }	
            printf("\n");


            for (i=0;i<NUMBINS;i++) {
                if ( histCnts[i] == histMax ) { 
                    printf("Center peak: %.3f\n", histBinEdges[i]);
                    break;
                }
            }
        }
        */

	// UDP packet should follow form.
	// udpPacket[0] = 10, index of first channel
	// udpPacket[1] = 10 + ? index of second channel
	// udpPacket[2] = total counts chan 1
	// udpPacket[3] = total counts chan 2
	// udpPacket[4] = basln 1
	// udpPacket[5] = basln 2
	// udpPacket[6] = std 1
	// udpPacket[7] = std 2
	// udpPacket[8] = p2p 1
	// udpPacket[9] = p2p 2
	// udpPacket[9] = age 1
	// udpPacket[9] = age 2
	// udpPacket[9] = dropped 1
	// udpPacket[9] = dropped 2


        //sprintf(udpPacket,"%u,%u",ch->particleCnt, (ch+1)->particleCnt);    //Status
        
        sprintf(udpPacket,"%u,%u,%u,%u,%u,%u,%u,%u,%u,%u,%llu,%llu,%u,%u", 14, 14+NUMBINS, ch->particleCnt, (ch+1)->particleCnt, \
            ((ch)->background->baseline), ((ch+1)->background->baseline), \
            ((ch)->background->std), ((ch+1)->background->std), \
            ((ch)->background->p2p), ((ch+1)->background->p2p), \
            globalLoopCt - ( (ch)->background->time ), \
            globalLoopCt - ( (ch+1)->background->time ),\
            ((ch)->buffersDropped), ((ch+1)->buffersDropped)); 
        
        for ( chNum = 0; chNum < 2; chNum++ ) {
            printf("CH1 Baselines: ");		
            for (j = 0; j < (ch + chNum)->background->baselinesHeld; j++) 
                printf("%u\t", *((ch + chNum)->background->bestBaselines+j));
            printf("\n"); 			
            printf("CH1 Variances: ");		
            for (j = 0; j < (ch + chNum)->background->baselinesHeld; j++) 
                printf("%lu\t", *((ch + chNum)->background->bestDeviations+j));
            printf("\n"); 			
            printf("CH1 P2Ps: ");		
            for (j = 0; j < (ch + chNum)->background->baselinesHeld; j++) 
                printf("%u\t", *((ch + chNum)->background->bestP2Ps+j));
            printf("\n"); 			
            printf("CH1 Times: ");		
            for (j = 0; j < (ch + chNum)->background->baselinesHeld; j++) 
                printf("%llu\t", *((ch + chNum)->background->bestTimes+j));
            printf("\n"); 			
            printf("Channel %u Particles: %u\t Scaled Particles: %u \n", \
                chNum, (ch + chNum)->particleCnt, \
                (unsigned int)(((float)((ch + chNum)->particleCnt))*4.35));;

            printf("Channel %u baselines held: %u\t Best Index: %d\t Worst Index: %d\n",\
                chNum, (ch + chNum)->background->baselinesHeld, \
                (ch+chNum)->background->bestIndex, \
                (ch+chNum)->background->worstIndex );
            printf("\n");

            for (i=0;i<NUMBINS;i++) {
                sprintf(tmpStr, ",%u",(ch + chNum)->histogram->histCnts[i]);
                strcat(udpPacket, tmpStr);
            }
        }
        strcat(udpPacket, "\r\n");
        Write_UDP(UDP0S, 0, udpPacket);
    } // End of infinite run loop
 
    for( chNum = 1; chNum >= 0; chNum-- ) {
        
        free((ch + chNum)->background->bestDeviations); // Array containing absolute values of difference between stgTwoLPF and raw data
        free((ch + chNum)->background->bestBaselines); // Array containing absolute values of either average of window OR single stgTwoLPF point
        free((ch + chNum)->background->bestTimes); // Array containing time at which baseline was stored...
        free((ch + chNum)->background->bestP2Ps); // Array containing time at which baseline was stored...
        free((ch + chNum)->background->bestSkews); // Array containing time at which baseline was stored...
        free((ch + chNum)->background->bestKurts); // Array containing time at which baseline was stored...

        free((ch + chNum)->background);
        free((ch + chNum)->particle);
        free((ch + chNum)->histogram);

        free((ch + chNum)->buf);
        free((ch + chNum)->lpf);
    }
    free(ch);
    free(buf);
    free(buf2);
    free(buf3);

    /* Done, close mappings, file and free the buffers */
    beaglelogic_munmap(bfd, bl_mem);
    beaglelogic_close(bfd);
	
    Close_UDP_Socket(UDP0S);
    closeFiles();

    printf("Full completion condition\n");

    return 0;
}






















