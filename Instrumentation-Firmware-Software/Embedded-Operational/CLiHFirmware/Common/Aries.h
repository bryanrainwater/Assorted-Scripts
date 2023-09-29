/*

	ARIES.H
	
	Diamond Systems Corporation Universal Driver
	Version 7.00

	(c) Diamond Systems Corporation 2012
	
	http://www.diamondsystems.com

	(c) Copyright 2012 Diamond Systems Corporation. Use of this source code
	is subject to the terms of Diamond Systems' Software License Agreement.
	Diamond Systems provides no warranty of proper performance if this
	source code is modified.
*/


#ifndef _DSC_ARIES_H_
#define _DSC_ARIES_H_

#include "common.h"

#ifdef DSC_ARIES_SUPPORT  /* only do the whole include if we are going to support ARIES */


#ifdef __cplusplus
extern "C" {
#endif
//Temperature Sensor
#define ARIES_TEMPERATURE_SENSOR_PAGE 5
#define ARIES_READ_SENSOR_BUSY_WAIT_OFFSET 10
#define ARIES_WRITE_SENSOR_CMD_OFFSET 10
#define ARIES_READ_SENSOR_WAIT_BIT 7
#define ARIES_READ_SENSOR_DATA_OFFSET 11 

//AD pages
#define ARIES_AD_BLOCK_PAGE						0
#define ARIES_WRITE_AD_CHANNEL_OFFSET  			2
#define ARIES_WRITE_AD_INPUT_MODE_OFFSET		3
#define ARIES_WRITE_AD_RANGE_OFFSET				4
#define ARIES_WRITE_AD_SCANEN_OFFSET			6
#define ARIES_WRITE_AD_SCANINTERVAL_OFFSET		7
#define ARIES_READ_AD_BUSY_WAIT_OFFSET			3
#define ARIES_AD_WAIT_BIT						6
#define ARIES_WRITE_AD_CLK_EN_OFFSET			5
#define ARIES_WRITE_AD_START_OFFSET				0
#define ARIES_AD_BUSY_BIT						7
#define ARIES_READ_AD_LSB_DATA_OFFSET			0
#define ARIES_READ_AD_MSB_DATA_OFFSET			1
#define ARIES_ADCAL_DEFAULT_TOLERANCE			2
#define ARIES_ADCAL_DEFAULT_DELAY_20MS			20
#define ARIES_FIFO_EMPTY						11

//DA pages
#define ARIES_DA_BLOCK_PAGE                     1
#define	ARIES_DASTATUS_READ						7
#define ARIES_DA_READ_BIT_DACBUSY				4
#define ARIES_NUMBER_OF_DA_CHANNEL				4
#define ARIES_MAX_RANGE_VALUE					6
#define ARIES_DAPAGE							1
#define ARIES_CURRENT_RANGE_DEFAULT_GAIN		0xFE00
#define ARIES_CURRENT_RANGE_DEFAULT_OFFSET		0x8000
#define ARIES_READ_BIT_DACBUSY					4
#define ARIES_DACODE_LSB						0
#define ARIES_DACODE_MSB							1

//Waveform pages
#define ARIES_WRITE_WGCMD					0x0B
#define ARIES_WRITE_WGCFG					0x0A
#define ARIES_WRITE_WGLSB					0x08
#define ARIES_WRITE_WGMSB					0x09
#define ARIES_FRAME_COUNT_LSB_REGISTER		0x0C
#define ARIES_FRAME_COUNT_MSB_REGISTER		0x0D

//Counter
#define ARIES_COUNTER_CMD_CLEAR					0x00
#define ARIES_COUNTER_NUMBER_REGISTER				4
#define ARIES_COUNTER_CMD_REGISTER					5
#define ARIES_COUNTER_CMD_RESET_ONE				0xF0
#define ARIES_COUNTER_DATA_BYTE0					0
#define ARIES_COUNTER_DATA_BYTE1					1
#define ARIES_COUNTER_DATA_BYTE2					2
#define ARIES_COUNTER_DATA_BYTE3					3
#define  ARIES_COUNTER_CMD_CLKSELECT		0x60
#define  ARIES_COUNTER_50MHZ 			50000000
#define  ARIES_COUNTER_1MHZ  			1000000
#define ARIES_COUNTER_AUTO_RELOAD_ENABLE         0x71
#define ARIES_COUNTER_CMD_LOAD					0x10
#define ARIES_COUNTER_CMD_SEL_DIRECTION_DOWN		0x20
#define ARIES_COUNTER_CMD_SEL_DIRECTION_UP		0x21
#define ARIES_COUNTER_CMD_EXTGATE_DISABLE		0x30
#define ARIES_COUNTER_CMD_EXTGATE_ENABLE			0x31
#define ARIES_COUNTER_DISABLE_OUTPUT             	0x80
#define ARIES_COUNTER_CMD_OUTPULSE_WIDTH		0x90
#define ARIES_COUNTER_CMD_COUNTER_ENABLE			0x41
#define ARIES_COUNTER_CMD_COUNTER_DISABLE		0x40
#define ARIES_COUNTER_AUTO_RELOAD_SET            0x70
#define ARIES_COUNTER_CMD_COUNTER_LATCH			0x50




//PWM
#define ARIES_CTRPWMPAGE					3
	#define  ARIES_PWM_CMD_REG	   	0x0B
#define ARIES_PWM_STOP_CURRENT_PWM	0x08
#define ARIES_PWM_SELECT_50MHZ_CLOCK_SOURCE 	0x60
#define ARIES_PWM_SELECT_1MHZ_CLOCK_SOURCE           	0x61
#define  ARIES_PWM_DATA_LSB  			0x08
#define  ARIES_PWM_DATA_CSB  			0x09
#define  ARIES_PWM_DATA_MSB  			0x0A
#define  ARIES_PWM_LOAD_C0_COUNTER		0x10
#define  ARIES_PWM_LOAD_C1_COUNTER		0x18
#define  ARIES_PWM_POLARITY_HIGH				0x20
#define  ARIES_PWM_POLARITY_LOW				0x28
#define  ARIES_PWM_ENABLE              0x38
#define  ARIES_PWM_ENABLE_OUTPUT_ON_DIO	    0x58
#define  ARIES_PWM_DISABLE_OUTPUT_ON_DIO       0x50
#define  ARIES_PWM_DISABLE					    0x30
#define  ARIES_PWM_START               0x70
#define  ARIES_MAX_PWM						    04
#define  ARIES_PWM_STOP_SELECTED_PWM  		    0x08
#define  ARIES_PWM_CLEAR_SELECTED_PWM			0x40
#define ARIES_PWM_CLEAR_ALL_PWM					0x48


//DIO pages
#define ARIES_DIO_BLOCK_PAGE				0x2
#define ARIES_MAX_DIO_PORTS     		    3
#define ARIES_DIO_A_DIR_REG_OFFSET			0x08
#define ARIES_DIO_PORT_A						0
#define ARIES_UNSIGNED_BYTE_MAX 			255 		// maximum value of an unsigned byte
#define ARIES_BITS_IN_BYTE_MAX  			7   // maximum bit indices in a byte (0-7)
#define ARIES_BIT_LOW          				0   // 0 represents a bit setting of low
#define ARIES_BIT_HIGH	    				1   // 1 represents a bit setting of high

//FIFO pages
#define ARIES_FIFO_BLOCK_PAGE					4
#define ARIES_FIFO_ENABLE_OFFSET					12
#define ARIES_FIFO_RESET_OFFSET					13
#define ARIES_FIFO_THRESHOLD_LSB_OFFSET			0
#define ARIES_FIFO_THRESHOLD_MSB_OFFSET			1
#define ARIES_FIFO_DEPTH_LSB_REG					4		
#define ARIES_FIFO_DEPTH_MSB_REG					5
#define ARIES_FIFO_FLAGS_REG						13

// EEPROM
#define ARIES_EEPROM_BLOCK_PAGE					5
#define ARIES_EEPROM_TDBUSY_BIT					6
#define ARIES_EEPROM_BUSY_OFFSET				7
#define ARIES_EEPROM_BUSY_BIT 					7
#define ARIES_EEPROM_ADDRESS_LSB_OFFSET			0
#define ARIES_EEPROM_ADDRESS_MSB_OFFSET			1
#define ARIES_EEPROM_COMMAND_OFFSET				6
#define ARIES_EEPROM_READ_COMMAND				0xC0
#define ARIES_EEPROM_WRITE_COMMAND				0x80
#define ARIES_EEPROM_UNLOCK_CODE_A_OFFSET		8
#define	ARIES_EEPROM_UNLOCK_CODE_B_OFFSET		9
#define ARIES_EEPROM_DATA_OFFSET				4
#define ARIES_EEPROM_TRIMDAC_EN_CMD				0x08
#define ARIES_EEPROM_CALMUX_EN_OFFSET			7


// Interrupt page
#define  ARIES_FPGAIDMinor_OFFSET	  			11
#define  ARIES_FPGAIDMajor_OFFSET	  			12
#define  ARIES_FPGA_ID_MAJOR_VALUE	  0x0F
#define  ARIES_FPGA_ID_MINOR_VALUE	  0x01
#define  ARIES_FPGARev_OFFSET		  			13
#define  ARIES_BoardIDMinor_OFFSET	   			8
#define  ARIES_BoardIDMajor_OFFSET	   			9
#define  ARIES_BoardRevision_OFFSET	  			10
#define  ARIES_INTERRUPT_NUM_OFFSET    			3
#define  ARIES_INTERRUPT_PAGE		   			7
#define  ARIES_INTERRUPT_INTEN_OFFSET  			0
#define  ARIES_INTERRUPT_INTCLR_OFFSET 			1
#define ARIES_INTERRUPT_DIO_EDGE_BIT_SEL_OFFSET 2
#define  ARIES_LED_OFFSET			   			4

// Board feature page 
#define ARIES_Board_Feature_Page 				8
#define CounterA_LSB_Offset						8
#define CounterA_MSB_Offset						9
#define CounterB_Offset							10
#define WD_Config_Offset						11
#define WD_INTERRUPT_INTCLR_OFFSET					11


// capablity pages
#define ARIES_CAPABILITY_BLOCK_PAGE			 15
#define AD_Chip_Present_Offset				 0
#define DA_Chip_Present_Offset			 	 2

//Miscellaneous 

#define ARIES_MAX_PAGE				16
#define ARIES_PAGENO_OFFSET 			15

//ARIESINIT

typedef struct
{
		int Address;        /*Base address assigned to board in PCI I/O memory space*/
		int IRQ;			/*IRQ number assigned to board*/
		int Slot;			/*FeaturePak slot number read from SlotID pins of module*/
		int FPGAIDMajor	;	/*FPGA ID major value*/
		int FPGAIDMinor;	/*FPGA ID minor value*/
		int FPGARev;		/*FPGA Revision value*/
		int BoardIDMajor;	/*Board ID major value*/
		int BoardIDMinor;	/*Board ID minor value*/
		int BoardRev;	    /*Board Revision value*/
		char* SerNo;		/*Serial number string*/
		char* Date;			/*Date of last factory calibration in BCD format, YYYYMMDD*/
		int ADChannels;     /* A/D chip presence / number of channels indicator */
		int DAChannels;		/*D/A chip presence / number of channels indicator */
		
}ARIESINIT;

typedef struct
{

	int 			CtrNo	;		//Counter number, 0-7
	unsigned long 	CtrData;		//Initial load data, 32-bit straight binary
	int 			CtrClock	;	//Clock source, must be 2 or 3 (see FPGA specification for usage)
	int 			CtrOutEn;		//1 = enable output onto corresponding I/O pin; 0 = disable output
	int 			CtrOutPol	;	//1 = output pulses high, 0 = output pulses low; only used if CtrOutEn = 1
	int				CtrCountDir; /*0 = down counting, 1 = up  counting*/
	int				CtrReload;	/*0 = one-shot counting, 1 = auto-reload (repetitive counting, only works in count down mode)*/
	int				CtrCmd;		/*Counter command, 0-15 (see FPGA specification for available commands)*/
	int				CtrCmdData;	/*Auxiliary data for counter command, 0-3 (see FPGA specification for usage)*/
	float			Rate;
	int 			ctrOutWidth ; // 0-3   0 = 1 clocks, 1 = 10 clocks, 2 = 100 clocks, 3 = 1000 clocks , only used if  CtrOutEn = 1 and CtrClock = 2 or 3

}ARIESCOUNTER ;

//ARIESPWM

typedef struct
{
		int Num;				/*PWM number, 0-3*/
		float Rate;		/*output frequency in Hz*/
		float Duty;			/*initial duty cycle, 0-100*/
		int Polarity;		/*0 = pulse high, 1 = pulse low*/
		int OutputEnable;	/*0 = disable output, 1 = enable output on DIO pin*/
		int Run	;			/*0 = don\92t start PWM, 1 = start PWM*/
		int Command;			/*0-15 = PWM command*/
		int CmdData;		/*0 or 1 for auxiliary PWM command data (used for certain commands)*/
		int Divisor;		/*24-bit value for use with period and duty cycle commands*/

}ARIESPWM;

typedef struct
{
	int Gain;			//0-3: 0 = 1, 1 = 2, 2 = 4, 3 = 8
	int Polarity;	 	//0-1; 0 = bipolar, 1 = unipolar
	int Sedi;			//0-1; 0 = single-ended, 1 = differential
	int Lowch;			//Low channel, 0-15
	int Highch;			//High channel, 0-15
	int LoadCal;		//True/False; True = recall calibration settings after changing input range
	int ScanEnable;		//0 = disable, 1 = enable
	int ScanInterval;	//0 = 10us, 1 = 5us, 2 = 8us, 3 = programmable using ProgInt
	int ProgInt;			//0-255, used if Interval = 3

}ARIESADSETTINGS;

typedef struct
{
	int FIFOEnable;			//0 = disable; interrupt occurs after each sample / scan; 1 = enable; interrupt occurs on FIFO threshold flag
	int FIFOThreshold;		//0-2048, indicates level at which FIFO will generate an interrupt if FIFOEnable = 1
	int Cycle;				//0 = one shot operation, interrupts will stop when the selected no. of samples / scans are acquired; 1 = continuous operation until terminated
	int ADClk;				//0-3 selects A/D clock source
	int NumConversions;		//if Cycle = 0 this is the number of samples / scans to acquire; if Cycle = 1 this is the size of the circular buffer in samples / scans
	SWORD *ADBuffer;			//pointer to A/D buffer to hold the samples; the buffer must be greater than or equal to NumConversions x 1 if scan is disabled or NumConversions x Scansize if scan is enabled (Scansize is Highch \96 Lowch + 1)

}ARIESADINT;

typedef struct
{

	int OpStatus;			//0 = Interrupts not running, 1 = Interrupts running
	int NumConversions;		//Number of conversions since interrupts started
	int BufferPtr;			//Position in A/D storage buffer, used in continuous mode when buffer is being repetitively overwritten
	int Cycle;				//0 = one-shot operation, 1 = continuous operation
	int FIFODepth;			//Current FIFO depth pointer
	int UF;					//0 = no underflow, 1 = FIFO underflow (attempt to read was made when FIFO was empty)
	int OF;					//0 = no overflow, 1 = FIFO overflow (attempt to write into FIFO when FIFO was full)
	int FF;					//0 = FIFO not full, 1 = FIFO is full
	int TF;					//0 = number of A/D samples in FIFO is less than the programmed threshold, 1 = number of A/D samples in FIFO is equal to or greater than the programmed threshold
	int EF;					//0 = FIFO has unread data in it, 1 = FIFO is empty


}ARIESADINTSTATUS;

typedef struct
{

int *ChannelSelect;		//pointer to array of 1/0 flags to indicate which channels are being updated
int *DACodes;			//pointer to array of unsigned int containing the 16-bit D/A output codes

}ARIESDASCAN;

typedef struct
{
	int Threshold;		//Current FIFO programmed threshold
	int Depth;			//Current FIFO depth pointer
	int Enable;			//0 = FIFO is not currently enabled, 1 = FIFO is currently enabled
	int UF;				//0 = no underflow, 1 = FIFO underflow (attempt to read was made when FIFO was empty)
	int OF;				//0 = no overflow, 1 = FIFO overflow (attempt to write into FIFO when FIFO was full)
	int FF;				//0 = FIFO not full, 1 = FIFO is full
	int TF;				//0 = number of A/D samples in FIFO is less than the programmed threshold, 1 = number of A/D samples in FIFO is equal to or greater than the programmed threshold
	int EF;				//0 = FIFO has unread data in it, 1 = FIFO is empty

}ARIESFIFO;

typedef struct
{

	int	Enable;			//0 = disable interrupts, 1 = enable interrupts; if Enable = 0 then no other parameters are required
	void (*IntFunc) (void *parameter);	//pointer to user function to run when interrupts occur
	int 	Mode	;		//0 = alone, 1 = before standard function, 2 = after standard function
	int 	Source	;		//Selects interrupt source:	0 = A/D, 1 = unused, 2 = counter 2 output, 3 = counter 3 output, 4 = digital I/O
	int 	BitSelect;		//0-21 selects which DIO line to use to trigger interrupts; only used if Source = 4
	int 	Edge;			//1 = rising edge, 0 = falling edge; only used if Source = 4

}ARIESUSERINT;


typedef struct
{

	int Enable;			//0 = disable, 1 = enable
	int Polarity;		//0 = use native positive value, 1 = enable inverter circuit
	int Channel;		//0-7 = selected channel number of calibration multiplexor

}ARIESCALMUX;

typedef struct
{
	int Range;				//0-7 for single range or -1 for all ranges
	int BootSet	;			//0 = don\92t set boot range, 1 = set boot range
	int BootRange;			//0-7 for desired range to set as the boot range
	float *OffsetErrors	;	//array of offset error values (low end of scale) resulting from calibration procedure. Any range that is calibrated will have a non-zero value. Any range that is not calibrated will have its tolerance value set to 0.
	float *FullScaleErrors;	//array of full-scale error values resulting from calibration procedure. Any range that is calibrated will have a non-zero value. Any range that is not calibrated will have its tolerance value set to 0.
	int Express;			//0 = run full calibration procedure, 1 = enable express mode
	float Tolerance;			//0 = use driver default error tolerance, nonzero means use given tolerance
	int Result;				//0 = failure, 1 = success

}ARIESADCAL;

typedef struct
{

unsigned int 	*Waveform;	//pointer to array of 16-bit unsigned data; If multiple channels are being set up at the same time, the data must be previously interleaved by the program, i.e. ch. 0, ch. 1, ch. 2, ch. 0, ch. 1, ch. 2, \85; the array size must be equal to Frames x FrameSize; the array size must be no greater than 2048
int 			Frames	;	//total number of frames in the array
int				FrameSize;	//no. of channels to be driven = frame size
int				*Channels;	//List of channels to be driven by the waveform generator; the number of values in this array must be equal to FrameSize; channels can be in any sequence
int 			Clock	;	//0 = software increment; 1 = counter/timer 0 output; 2 = counter/timer 1 output; 3 = DIO pin D0
float 			Rate	;	//frame update rate, Hz (only used if Clock = 1 or 2)
int 			Cycle	;	//0 = one-shot operation; 1 = repetitive operation

}ARIESWAVEFORM;

typedef struct
{
int 	CtrAData;	           	 //1-65535 =16-bit timer value (runs at 100Hz - max 655.35 seconds) 
int 	CtrBData;	           	 //1-255 = 8-bit timer value (runs at 100Hz - max 2.55seconds) 
int 	HardwareTriggerEnable ;	 //0 = disable, 1 = enable 
int 	EdgeSelection;		  	 //if HardwareTriggerEnable = 1, then 0 = Raising edge 1 = falling edge 
int 	CountEarly	;	 	     //0 = disable, 1 = enable i.e. DIO C4 goes high when counter A = 1 instead 
								 //of 0 , This enables C4 to be externally wired to C5 to cause an 
								 //automatic repetitive retrigger when WDIEN = 1 and WDEDGE = 0
int 	InterruptEnable; 		 //1= when counter A reaches 0 an interrupt will occur, 0=interrupt 
								 //will not occur
void (*IntFunc) (void *parameter);	//pointer to user function to run when interrupts occur
}ARIESWATCHDOG;

/////////////////////////
// Function Prototypes //
/////////////////////////

BYTE ARIESMain(DSCB board, WORD func, void * params);

BYTE DSCUDAPICALL ARIESInitBoard(DSCCB* dsccb, ARIESINIT *Init);
BYTE DSCUDAPICALL ARIESFreeBoard(DSCB board);

BYTE DSCUDAPICALL ARIESADSetSettings(BoardInfo* bi, ARIESADSETTINGS* settings);
BYTE DSCUDAPICALL ARIESADSetRange(BoardInfo* bi, ARIESADSETTINGS* settings);
BYTE DSCUDAPICALL ARIESADSetChannel(BoardInfo* bi, ARIESADSETTINGS* settings);
BYTE DSCUDAPICALL ARIESADSetScan(BoardInfo* bi, ARIESADSETTINGS* settings);
BYTE DSCUDAPICALL ARIESADSetClock(BoardInfo* bi, BYTE ADClk);
BYTE DSCUDAPICALL ARIESADStartClock(BoardInfo* bi); //Enables the clock,change
BYTE DSCUDAPICALL ARIESADStopClock(BoardInfo* bi);
BYTE DSCUDAPICALL ARIESADSample(BoardInfo* bi, SWORD* Sample); //changed from unsigned * to int*
BYTE DSCUDAPICALL ARIESADScan(BoardInfo* bi, SWORD* Sample); //changed from unsigned * to int*
BYTE DSCUDAPICALL ARIESADInt(BoardInfo* bi, ARIESADINT* ariesadint);
BYTE DSCUDAPICALL ARIESADIntStatus(BoardInfo* bi, ARIESADINTSTATUS* intstatus);
BYTE DSCUDAPICALL ARIESADIntPause(BoardInfo* bi);
BYTE DSCUDAPICALL ARIESADIntResume(BoardInfo* bi);
BYTE DSCUDAPICALL ARIESADIntCancel(BoardInfo* bi);
BYTE DSCUDAPICALL ARIESADAutoCal(BoardInfo* bi, ARIESADCAL* Params);
BYTE DSCUDAPICALL ARIESADCalVerify(BoardInfo* bi, ARIESADCAL* Params);
BYTE DSCUDAPICALL ARIESFIFOStatus(BoardInfo* bi, ARIESFIFO* ARIESfifo);
BYTE DSCUDAPICALL ARIESADRead(BoardInfo* bi, SWORD* Sample);



BYTE DSCUDAPICALL ARIESUserInterruptConfig(BoardInfo* bi, ARIESUSERINT* ARIESuserint);
BYTE DSCUDAPICALL ARIESUserInterruptRun(BoardInfo* bi, int Source, int Bit, int Edge);
BYTE DSCUDAPICALL ARIESUserInterruptCancel(BoardInfo* bi, int Source);

BYTE DSCUDAPICALL ARIESDASetSettings(BoardInfo* bi, int Channel, int Range, int OverRange, int ClearEnable,int LoadCal);
BYTE DSCUDAPICALL ARIESDAConvert(BoardInfo* bi, int Channel, unsigned int DACode);
BYTE DSCUDAPICALL ARIESDAConvertScan(BoardInfo* bi, int* ChannelSelect, unsigned int * DACodes);
BYTE DSCUDAPICALL ARIESDAFunction(BoardInfo* bi, unsigned int DAData, int DACommand);
BYTE DSCUDAPICALL ARIESDAUpdate(BoardInfo* bi) ;
BYTE DSCUDAPICALL ARIESDARead(BoardInfo* bi,int chip,int Register, unsigned int* Value);
BYTE DSCUDAPICALL ARIESDASetSim(BoardInfo* bi, int Simup);
BYTE DSCUDAPICALL ARIESSetOffset(BoardInfo* bi, int Channel, unsigned int Offset);
BYTE DSCUDAPICALL ARIESSetGain(BoardInfo* bi, int Channel, unsigned int Gain);
BYTE DSCUDAPICALL ARIESSetClearCode(BoardInfo* bi, int Channel, unsigned int ClearCode);
BYTE DSCUDAPICALL ARIESSetSlew(BoardInfo* bi, int Channel, int Enable, int SlewClock, int SlewStep);

BYTE DSCUDAPICALL ARIESDIOConfig(BoardInfo* bi, int Port, int Config);
BYTE DSCUDAPICALL ARIESDIOConfigAll(BoardInfo* bi, int* Config);
BYTE DSCUDAPICALL ARIESDIOOutputByte(BoardInfo* bi, int port, BYTE data);
BYTE DSCUDAPICALL ARIESDIOInputByte(BoardInfo* bi, int port, BYTE* data);
BYTE DSCUDAPICALL ARIESDIOOutputBit(BoardInfo* bi, int port, int bit, int digital_value);
BYTE DSCUDAPICALL ARIESDIOInputBit(BoardInfo* bi, int port, int bit, int* digital_value);


BYTE DSCUDAPICALL ARIESCounterSetRate(BoardInfo* bi, ARIESCOUNTER *Ctr);
BYTE DSCUDAPICALL ARIESCounterFunction(BoardInfo* bi, ARIESCOUNTER *Ctr);
BYTE DSCUDAPICALL ARIESCounterRead(BoardInfo* bi, ARIESCOUNTER *Ctr);
BYTE DSCUDAPICALL ARIESCounterConfig(BoardInfo* bi, ARIESCOUNTER *Ctr);
BYTE DSCUDAPICALL ARIESCounterReset(BoardInfo* bi, int CtrNum);


BYTE DSCUDAPICALL ARIESPWMConfig(BoardInfo* bi, ARIESPWM* ariespwm);
BYTE DSCUDAPICALL ARIESPWMStart(BoardInfo* bi, int Num);
BYTE DSCUDAPICALL ARIESPWMStop(BoardInfo* bi, int Num);
BYTE DSCUDAPICALL ARIESPWMCommand(BoardInfo* bi, ARIESPWM* ARIESpwm);
BYTE DSCUDAPICALL ARIESPWMReset(BoardInfo* bi, int Num);
BYTE DSCUDAPICALL ARIESSetPage(BoardInfo* bi, BYTE page);
BYTE ARIESInputLong ( BoardInfo* bi, DWORD start_address, DWORD* data );

BYTE DSCUDAPICALL ARIESSetTrimDAC(BoardInfo* bi, int TrimDAC, int Value);
BYTE DSCUDAPICALL ARIESSetCalMux(BoardInfo* bi, ARIESCALMUX* Calmux);
BYTE DSCUDAPICALL ARIESLED(BoardInfo* bi, int Enable);

BYTE DSCUDAPICALL ARIESWaveformBufferLoad(BoardInfo* bi, ARIESWAVEFORM* ARIESwaveform);
BYTE DSCUDAPICALL ARIESWaveformDataLoad(BoardInfo* bi, int Address, int Channel, unsigned int Value);
BYTE DSCUDAPICALL ARIESWaveformConfig(BoardInfo* bi, ARIESWAVEFORM* ARIESwaveform);
BYTE DSCUDAPICALL ARIESWaveformStart(BoardInfo* bi);
BYTE DSCUDAPICALL ARIESWaveformPause(BoardInfo* bi);
BYTE DSCUDAPICALL ARIESWaveformReset(BoardInfo* bi);
BYTE DSCUDAPICALL ARIESWaveformInc(BoardInfo* bi);

BYTE DSCUDAPICALL ARIESGetReferenceVoltages(BoardInfo* bi, float* Refs);
BYTE DSCUDAPICALL ARIESSetReferenceVoltages(BoardInfo* bi, float* Refs);

BYTE DSCUDAPICALL ARIESEEPROMRead(BoardInfo* bi, int Address, int* Data);
BYTE DSCUDAPICALL ARIESEEPROMWrite(BoardInfo* bi, int Address, int Data);
BYTE DSCUDAPICALL ARIESEEPROMWriteX(BoardInfo* bi, int Address, int Data);

BYTE DSCUDAPICALL ARIESWatchDogConfig(BoardInfo* bi, ARIESWATCHDOG *settings);
BYTE DSCUDAPICALL ARIESWatchDogEnable(BoardInfo* bi);
BYTE DSCUDAPICALL ARIESWatchDogDisable(BoardInfo* bi);
BYTE DSCUDAPICALL ARIESWatchDogSoftwareReTrigger(BoardInfo* bi);

BYTE DSCUDAPICALL ARIESTemperatureSensorRead(BoardInfo* bi, BYTE cmd,signed int *Data);
#else //tells people that there's no ARIES

BYTE ARIESMain(DSCB board, WORD func, void * params);

#endif

#ifdef __cplusplus
} /* Closes the extern "C" */
#endif

#endif // #ifndef _DSC_ARIES_H_

