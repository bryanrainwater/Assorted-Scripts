/*

    COMMON.H

    Diamond Systems Corporation Universal Driver
    Version 7.00

    (c) Diamond Systems Corporation 2010

    http://www.diamondsystems.com

    (c) Copyright 2010 Diamond Systems Corporation. Use of this source code
    is subject to the terms of Diamond Systems' Software License Agreement.
    Diamond Systems provides no warranty of proper performance if this
    source code is modified.
*/


#ifndef _DSCCOMMON_H
#define _DSCCOMMON_H

//#ifdef WIN32
//#define DSCUDAPICALL __declspec(dllexport)
//#else /* WIN32 not defined */
//#define DSCUDAPICALL
//#endif /* #ifdef WIN32 */
#ifdef __cplusplus
extern "C"  DSCUDAPICALL BoardInfo*  DSCGetBoardInfo(DSCB handle);
#endif

#define DSC_ATHENA_SUPPORT
#define DSC_ATHENAII_SUPPORT
#define DSC_COOPER_SUPPORT
#define DSC_DMM_SUPPORT
#define DSC_DMMAT_SUPPORT
#define DSC_DMM16AT_SUPPORT
#define DSC_DMM32_SUPPORT
#define DSC_DMM32X_SUPPORT
#define DSC_DMM32DX_SUPPORT
#define DSC_DMM48_SUPPORT
#define DSC_DIO82C55_SUPPORT
#define DSC_ELEKTRA_SUPPORT
#define DSC_EMM8_SUPPORT
#define DSC_EMMDIO_SUPPORT
#define DSC_GMM_SUPPORT
#define DSC_GPIO11_SUPPORT
#define DSC_GPIO21_SUPPORT
#define DSC_HERC_SUPPORT
#define DSC_HELIOS_SUPPORT
#define DSC_IR104_SUPPORT
#define DSC_NEPTUNE_SUPPORT
#define DSC_OMM_SUPPORT
#define DSC_OMMDIO_SUPPORT
#define DSC_OPMM_SUPPORT
#define DSC_PMM_SUPPORT
#define DSC_PROM_SUPPORT
#define DSC_PSD_SUPPORT
#define DSC_QMM_SUPPORT
#define DSC_RAW_SUPPORT
#define DSC_RMM_SUPPORT
#define DSC_RMM416_SUPPORT
#define DSC_RMM1612_SUPPORT
#define DSC_TEST_SUPPORT
#define DSC_ZMM_SUPPORT
#define DSC_METIS_SUPPORT
#define DSC_FPDAQ1616_SUPPORT
#define DSC_FPGPIO96_SUPPORT
#define DSC_OPMM1616_SUPPORT
#define DSC_HELIOSDV_SUPPORT
#define DSC_VEGA_SUPPORT
#define DSC_ATHENAIII_SUPPORT
#define DSC_ALTAIR_SUPPORT
#define DSC_RMM1616_SUPPORT
#define DSC_MPEGPIO_SUPPORT
#define DSC_MPEDAQ0804_SUPPORT
#define DSC_EMMDIO4M_SUPPORT
#define DSC_ARIES_SUPPORT



#ifdef _WIN32_WCE
#include <windows.h>
#endif

#ifdef __RTCORE_KERNEL__

#define strcpy rtl_strcpy

#include <rtl_string.h>
#include <rtl_stdlib.h>

#ifndef memset
#define memset rtl_memset
#endif

#ifndef memcpy
#define memcpy rtl_memcpy
#endif

double sqrt(double x);
int abs(int x);
long int labs(long int x);
double fabs(double x);
double floor(double x);

#endif

#ifndef __RTCORE_KERNEL__
#include <string.h>
#include <math.h>
#include <stdlib.h>
#endif

#ifndef BZERO
#define BZERO(buf) memset(&(buf), 0, sizeof(buf))
#endif

#include "dscud.h"
#include "dscud_os.h"

////////////////////////////
// DSCUD Internal Defines //
////////////////////////////

#define LOCK_TIMEOUT 3000 // Milliseconds before an attempt to aquire a board fails
#define OP_TIMEOUT   3000 // Milliseconds for a standard op to timeout
#define DSC_OP_DELAY 10   // Milliseconds to wait for minor operations that need settling


///////////////////////////////////////////////////////////////////////////////
// DSCUDKP Message Codes (must match those defined in "../dscudkp/dscudkp.h" //
///////////////////////////////////////////////////////////////////////////////

#define DSCUDKP_GET_BUFFER          0
#define DSCUDKP_GET_NUM_TRANSFERS   1
#define DSCUDKP_SET_DRV_CONTEXT     2
#define DSCUDKP_GET_DRV_CONTEXT     3
#define DSCUDKP_FREE_BUFFER         4
#define DSCUDKP_SET_BUFFER          5
#define DSCUDKP_GET_DIO_BUFFER      6
#define DSCUDKP_GET_FIFO_OVERFLOW   7


//////////////////////
// Internal Structs //
//////////////////////

typedef struct {

    float hertz;
    DWORD ctr;

} DSCCSRS; //DSC Counter Set Rate Single


typedef struct {

    DFLOAT* offsets;
    int count;

} DSCDAOFFSETS;


typedef struct {

    BYTE port;
    BYTE digital_value;
    WORD digital_word;
    BYTE bit;
    BYTE portConfig;
} DIOPARAMS;


typedef struct {

    BOOL dout;
    BOOL dstate;
    BOOL cstate;

} PICPROGSET;


typedef struct {

    DWORD address;
    DSCDACODE value;
    DWORD channel;
    BOOL simul;

} WGBUFFERSET;

// first used in opmm1616
typedef struct {

    BYTE cmdName;
    BYTE cmdValue;

} COMMANDPARAMS;

//////////////////////
// DSCFP_BOARD_CONFIG
//////////////////////
typedef struct
{
    BYTE adChannels ;   /* Number of AD channels supported by the board*/
    BYTE daChannels ;   /* Number of DA channels supported by the board*/
    BYTE dioPorts ;     /* Number of DIO ports supported by the board*/
    WORD wFPGARev ;     /* 2 byte FPGA rev of the board */
    WORD wBoardID ;     /* 2 byte board ID */
} DSCFP_BOARD_CONFIG;

////////////////////////
// Function Constants //
////////////////////////

#define DRVRFUNCTIONS          0x0000
#define A2DFUNCTIONS           0x1000
#define D2AFUNCTIONS           0x2000
#define DIOFUNCTIONS           0x3000
#define A9513FUNCTIONS         0x4000
#define CTRFUNCTIONS           0x5000
#define AUTOCALFUNCTIONS       0x6000
#define OTHERFUNCTIONS         0x7000
#define OPTOFUNCTIONS          0x8000

#define DSINIT                 DRVRFUNCTIONS+0
#define DSFREE                 DRVRFUNCTIONS+1
#define DSINITBOARD            DRVRFUNCTIONS+2
#define DSFREEBOARD            DRVRFUNCTIONS+3
#define DRVRTEST               DRVRFUNCTIONS+4
#define DSPCIINITBOARD         DRVRFUNCTIONS+5

#define DSADSETSETTINGS        A2DFUNCTIONS+0
#define DSADSAMPLE             A2DFUNCTIONS+1
#define DSADSCAN               A2DFUNCTIONS+2
#define DSADSAMPLEINT          A2DFUNCTIONS+3
#define DSADSCANINT            A2DFUNCTIONS+4
#define DSADSAMPLEDMA          A2DFUNCTIONS+5
#define DSADSETCHANNEL         A2DFUNCTIONS+6
#define DSADSETSCAN            A2DFUNCTIONS+7
#define DSADSETGAINTABLE       A2DFUNCTIONS+8
//Added

//Upto

#define DSADAUTOCAL            AUTOCALFUNCTIONS+0
#define DSADCALVERIFY          AUTOCALFUNCTIONS+1
#define DSSETCALCHANNEL        AUTOCALFUNCTIONS+2
#define DSMEASUREREFERENCES    AUTOCALFUNCTIONS+3
#define DSDAAUTOCAL            AUTOCALFUNCTIONS+4
#define DSDACALVERIFY          AUTOCALFUNCTIONS+5
#define DSDAAUTOCAL2           AUTOCALFUNCTIONS+6
#define DSDACALVERIFY2         AUTOCALFUNCTIONS+7
#define DSSETTDAC              AUTOCALFUNCTIONS+8
#define DSDASETPROGREF         AUTOCALFUNCTIONS+9
#define DSDASETPROGVOLTAGE     AUTOCALFUNCTIONS+10
#define DSDACALCHANNELOFFSETS  AUTOCALFUNCTIONS+11
#define DSGETREFS              AUTOCALFUNCTIONS+12
#define DSSETREFS              AUTOCALFUNCTIONS+13
#define DSSETCALMUX            AUTOCALFUNCTIONS+14
#define DSGETREFVOLTAGES       AUTOCALFUNCTIONS+15
#define DSSETREFVOLTAGES       AUTOCALFUNCTIONS+16
#define DSGETOFFSETS           AUTOCALFUNCTIONS+17
#define DSSETOFFSETS           AUTOCALFUNCTIONS+18
#define DSAACCOMMAND           AUTOCALFUNCTIONS+19
#define DSAACGETSTATUS         AUTOCALFUNCTIONS+20
#define DSPICOUTP              AUTOCALFUNCTIONS+21
#define DSPICINP               AUTOCALFUNCTIONS+22
#define DSPICPROGENABLE        AUTOCALFUNCTIONS+23
#define DSPICPROGSET           AUTOCALFUNCTIONS+24
#define DSPICPROGGET           AUTOCALFUNCTIONS+25
#define DSDAMONSEL             AUTOCALFUNCTIONS+25

#define DSDASETPOLARITY        D2AFUNCTIONS+0
#define DSDACONVERT            D2AFUNCTIONS+1
#define DSDACONVERTSCAN        D2AFUNCTIONS+2
#define DSDACONVERTSCANINT     D2AFUNCTIONS+3
#define DSDASETTINGS           D2AFUNCTIONS+4
#define DSWGCOMMAND            D2AFUNCTIONS+5
#define DSWGCONFIGSET          D2AFUNCTIONS+6
#define DSWGCONFIGGET          D2AFUNCTIONS+7
#define DSWGBUFFERSET          D2AFUNCTIONS+8
#define DSDAFUNCTION           D2AFUNCTIONS+9
#define DSDAUPDATE             D2AFUNCTIONS+10

#define DSDIOSETCONFIG         DIOFUNCTIONS+0
#define DSDIOINPUTBYTE         DIOFUNCTIONS+1
#define DSDIOOUTPUTBYTE        DIOFUNCTIONS+2
#define DSDIOINPUTWORD         DIOFUNCTIONS+3
#define DSDIOOUTPUTWORD        DIOFUNCTIONS+4
#define DSDIOINPUTBIT          DIOFUNCTIONS+5
#define DSDIOSETBIT            DIOFUNCTIONS+6
#define DSDIOCLEARBIT          DIOFUNCTIONS+7
#define DSDIOINPUTINT          DIOFUNCTIONS+8
#define DSDIOOUTPUTINT         DIOFUNCTIONS+9
#define DSDIOOUTPUTBIT         DIOFUNCTIONS+10
#define DSINNERDIOOUTPUTBYTE   DIOFUNCTIONS+11
#define DSINNERDIOINPUTBYTE    DIOFUNCTIONS+12
#define DSDIOGETCONFIG         DIOFUNCTIONS+13
#define DSDIOSETPORTCONFIG     DIOFUNCTIONS+14
#define DSDIOGETPORTCONFIG     DIOFUNCTIONS+15

#define DSRELAYSET             DIOFUNCTIONS+100
#define DSRELAYGET         DIOFUNCTIONS+101
#define DSRELAYSETMULTI        DIOFUNCTIONS+102
#define DSRELAYGETMULTI        DIOFUNCTIONS+103

#define DSOPTOINPUTBYTE        OPTOFUNCTIONS+0
#define DSOPTOINPUTBIT         OPTOFUNCTIONS+1
#define DSOPTOGETPOLARITY      OPTOFUNCTIONS+2

#define DSOPTOGETSTATE         OPTOFUNCTIONS+10
#define DSOPTOSETSTATE         OPTOFUNCTIONS+11

#define DSCOUNTERSETRATE        CTRFUNCTIONS+0
#define DSCOUNTERDIRECTSET      CTRFUNCTIONS+1
#define DSCOUNTERREAD           CTRFUNCTIONS+2
#define DSOMMCONFIGURECOUNTERS  CTRFUNCTIONS+3
#define DSCOUNTERSETRATESINGLE  CTRFUNCTIONS+4
#define DSCOUNTERFUNCTION       CTRFUNCTIONS+5

#define DS9513SETMMR           A9513FUNCTIONS+0
#define DS9513SETCMR           A9513FUNCTIONS+1
#define DS9513COUNTERCONTROL   A9513FUNCTIONS+2
#define DS9513GETSTATUS        A9513FUNCTIONS+3
#define DS9513SETCLR           A9513FUNCTIONS+4
#define DS9513SETCHR           A9513FUNCTIONS+5
#define DS9513GETCHR           A9513FUNCTIONS+6
#define DS9513SPECIALCOUNTER   A9513FUNCTIONS+7
#define DS9513SETCOUNTERALARM  A9513FUNCTIONS+8
#define DS9513COUNTERINT       A9513FUNCTIONS+9
#define DS9513MEASUREFREQUENCY A9513FUNCTIONS+10
#define DS9513MEASUREPERIOD    A9513FUNCTIONS+11
#define DS9513RESET            A9513FUNCTIONS+12
#define DS9513PWM              A9513FUNCTIONS+13
#define DS9513SCC              A9513FUNCTIONS+14

#define DSUSERINT              OTHERFUNCTIONS+0
#define DSGETSTATUS            OTHERFUNCTIONS+1
#define DSCANCELOP             OTHERFUNCTIONS+2
#define DSPAUSEOP              OTHERFUNCTIONS+3
#define DSRESUMEOP             OTHERFUNCTIONS+4
#define DSENABLEUSERINTS       OTHERFUNCTIONS+5
#define DSDISABLEUSERINTS      OTHERFUNCTIONS+6
#define DSREGISTERWRITE        OTHERFUNCTIONS+7
#define DSREGISTERREAD         OTHERFUNCTIONS+8
#define DSDISABLEINTS          OTHERFUNCTIONS+9
#define DSGETERRORSTRING       OTHERFUNCTIONS+10
#define DSREGISTERREADBACK     OTHERFUNCTIONS+11
#define DSGETEEPROM            OTHERFUNCTIONS+12
#define DSSETEEPROM            OTHERFUNCTIONS+13
#define DSEMMDIOSETSTATE       OTHERFUNCTIONS+14
#define DSEMMDIOGETSTATE       OTHERFUNCTIONS+15
#define DSSETUSERINTFUNC       OTHERFUNCTIONS+16
#define DSCLEARUSERINTFUNC     OTHERFUNCTIONS+17
#define DSEMMDIOSETINT         OTHERFUNCTIONS+18
#define DSWATCHDOGENABLE       OTHERFUNCTIONS+19
#define DSWATCHDOGDISABLE      OTHERFUNCTIONS+20
#define DSWATCHDOGTRIGGER      OTHERFUNCTIONS+21
#define DSEMMDIORESETINT       OTHERFUNCTIONS+22
#define DSPWMLOAD              OTHERFUNCTIONS+23
#define DSPWMCONFIG            OTHERFUNCTIONS+24
#define DSPWMCLEAR             OTHERFUNCTIONS+25
#define DSPULSEWIDTHMOD        OTHERFUNCTIONS+26
#define DSSETTRIMDAC           OTHERFUNCTIONS+27
#define DSGETTRIMDAC           OTHERFUNCTIONS+28
#define DSENHANFEAT            OTHERFUNCTIONS+29
#define DSINTERRUPTCONTROL     OTHERFUNCTIONS+30
#define DSINTERRUPTSRCSELECT   OTHERFUNCTIONS+31

// NEW CONSTANST FOR NEW APIs IN FPDAQ1616 BOARD
#define DSFPCAPABILITIESREAD   OTHERFUNCTIONS+32
#define DSFPCOMMAND            OTHERFUNCTIONS+33
#define DSFPBOARDRESET         OTHERFUNCTIONS+34
#define DSFPGETBRDCFG          OTHERFUNCTIONS+35
#define DSCRESTORECALIBRATION  OTHERFUNCTIONS+36
#define DSCOMMAND              OTHERFUNCTIONS+37 // OPMM-1616
#define DSINTCONFIG            OTHERFUNCTIONS+38 // OPMM-1616
#define DSDIOCTRMODE           OTHERFUNCTIONS+39 // FP-GPIO-96
#define DSSETPAGE              OTHERFUNCTIONS+40
// New Constant for Altair PWM Control
#define DSPWMCOMMAND		   OTHERFUNCTIONS+41
#define DSPWMCONTROL		    OTHERFUNCTIONS+42

//////////////////////////////////////////////
// PWM BLOCK DEFINES
//////////////////////////////////////////////
#define PWM_BLOCK_OFFSET                48
#define PWM_MAX_NUM                     4
#define PWM_FREQUENCY_MAXIMUM_SOURCE0   50000000L
#define PWM_FREQUENCY_MAXIMUM_SOURCE1   1000000L
#define PWM_FREQUENCY_MINIMUM           0.059604648L
#define PWM_COMMAND_MASK                0xF8
#define PWM_COMMAND_REGISTER            11
#define PWM_DATA_LSB                    8
#define PWM_DATA_CSB                    9
#define PWM_DATA_MSB                    10
#define PWM_COUNTER_C0                  0
#define PWM_COUNTER_C1                  1

// PWM command masks
#define PWM_LOAD_C0_COUNTER                 0x10
#define PWM_LOAD_C1_COUNTER                 0x18
#define PWM_POLARITY_HIGH                   0x20
#define PWM_POLARITY_LOW                    0x28
#define PWM_DISABLE_PULSE_OUTPUT            0x30
#define PWM_ENABLE_PULSE_OUTPUT             0x38
#define PWM_STOP_CURRENT_PWM                0x40
#define PWM_STOP_ALL_PWMS                   0x48
#define PWM_DISABLE_OUTPUT_ON_DIO_PORT_F    0x50
#define PWM_ENABLE_OUTPUT_ON_DIO_PORT_F     0x58
#define PWM_SELECT_50MHZ_CLOCK_SOURCE       0x60
#define PWM_SELECT_1MHZ_CLOCK_SOURCE        0x68
#define PWM_START_CURRENT_PWM               0x70
#define PWM_START_ALL_PWMS                  0x7F
#define PWM_SELECTED_MASK                   0x07
#define PWM_COUNTING_PERIOD_MAX             16777215.0

/////////////////////////
// Function Prototypes //
/////////////////////////
BYTE DSCPCIBoardType(WORD deviceID, BYTE * boardtype);
int DSCStringEquals(char* str1, char* str2);
char DSCToUpper(char c);
DWORD GetIntIndex(DWORD int_type);
BYTE DSCSetIntInfo(BoardInfo * bi);
WORD DSCGetCounterFactor(DWORD count);
DSCUDAPICALL BoardInfo*  DSCGetBoardInfo(DSCB handle);
BYTE DSCSetLastError(BYTE error_code, const char* error_str);
BYTE DSCGetLastError(ERRPARAMS* errparams);
BYTE DSCGetErrorString(ERRPARAMS* errparams);

DSCB DSCQueryNextBoard(void);

BYTE  DSCLockBoard(DSCB board);
BYTE DSCUnlockBoard(DSCB board);

BYTE DSCGetStatus(BoardInfo* bi, DSCS* status);
BYTE DSCCancelOp(BoardInfo* bi, DWORD int_type);
BYTE DSCPauseOp(BoardInfo* bi);
BYTE DSCResumeOp(BoardInfo* bi);

BYTE DSCFlipFlopReset(BoardInfo* bi, DWORD int_type);

// Extern Definitiions
extern BYTE DSCUDAPICALL dscPWMFnc(DSCB board, DSCPWM* dscpwm);

//Generic Read writes 
BYTE DSCUDAPICALL ISARegisterWrite(BoardInfo* bi, int Page, int Register, int Value);
BYTE DSCUDAPICALL ISARegisterRead(BoardInfo* bi, int Page, int Register, int* Value);

BYTE DSCUDAPICALL PCIRegisterWrite(BoardInfo* bi, int Page, int Register, int Value);
BYTE DSCUDAPICALL PCIRegisterRead(BoardInfo* bi, int Page, int Register, int* Value);


#endif // #ifndef _COMMON_H

