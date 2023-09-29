/*

	DAQ0804.H

	Diamond Systems Corporation Universal Driver
	Version 7.00

	(c) Diamond Systems Corporation 2013

	http://www.diamondsystems.com

	(c) Copyright 2013 Diamond Systems Corporation. Use of this source code
	is subject to the terms of Diamond Systems' Software License Agreement.
	Diamond Systems provides no warranty of proper performance if this
	source code is modified.
*/


#ifndef _DSC_DAQ0804_H
#define _DSC_DAQ0804_H

#include "common.h"

#ifdef DSC_MPEDAQ0804_SUPPORT /* only do the whole include if we are going to support DAQ0804 */

#ifdef __cplusplus
extern "C" {
#endif

///////////////////////
// DAQ0804 Constants //
///////////////////////

// Capablities ReadBack registers
#define DAQ0804_AD_PRESENT_OFFSET				0xF0
#define DAQ0804_DA_PRESENT_OFFSET				0xF2

//Interrupt Block Defines
#define DAQ0804_INTERRUPT_BLOCK_OFFSET				0x70
#define DAQ0804_INTERRUPT_ENABLE_OFFSET				DAQ0804_INTERRUPT_BLOCK_OFFSET + 0
#define DAQ0804_INTERRUPT_INTCLR_OFFSET 			DAQ0804_INTERRUPT_BLOCK_OFFSET + 1
#define DAQ0804_INTERRUPT_DIO_EDGE_BIT_SEL_OFFSET		DAQ0804_INTERRUPT_BLOCK_OFFSET + 2
#define DAQ0804_BDRST_OFFSET						DAQ0804_INTERRUPT_BLOCK_OFFSET+0x0F
#define DAQ0804_BOARD_MAJOR_ID_OFFSET				DAQ0804_INTERRUPT_BLOCK_OFFSET+0x09
#define DAQ0804_BOARD_MAJAOR_ID_VALUE				0X0C
#define	DAQ0804_FPGA_MAJOR_ID_OFFSET				DAQ0804_INTERRUPT_BLOCK_OFFSET+0x0D
#define DAQ0804_FPGA_MINOR_ID_OFFSET				DAQ0804_INTERRUPT_BLOCK_OFFSET+0x0C
#define DAQ0804_LED_OFFSET							0x74
#define DAQ0804_PIC_CONFIG_OFFSET 					0x75

// AD BLOCK DEFINES
#define DAQ0804_AD_BLOCK_OFFSET						0x00
#define DAQ0804_AD_RANGE_REG						DAQ0804_AD_BLOCK_OFFSET + 0x08
#define DAQ0804_AD_DATA_LSB_REG						DAQ0804_AD_BLOCK_OFFSET + 0x00
#define DAQ0804_AD_DATA_MSB_REG						DAQ0804_AD_BLOCK_OFFSET + 0x01
#define DAQ0804_AD_LOW_CHANNEL_REG					DAQ0804_AD_BLOCK_OFFSET + 0x04
#define DAQ0804_AD_HIGH_CHANNEL_REG					DAQ0804_AD_BLOCK_OFFSET + 0x05
#define DAQ0804_AD_TIMING_REG						DAQ0804_AD_BLOCK_OFFSET + 0x0A
#define DAQ0804_AD_SCAN_INTERVAL_REG				DAQ0804_AD_BLOCK_OFFSET + 0x0B
#define DAQ0804_AD_START_AD_CONVERSION_REG			DAQ0804_AD_BLOCK_OFFSET + 0x00
#define DAQ0804_AD_START_AD_CONVERSION_CMD			0x01
#define DAQ0804_AD_ADCMD							0x04
#define DAQ0804_AD_STATUS_OFFSET					DAQ0804_AD_BLOCK_OFFSET + 0x03
#define DAQ0804_AD_ADBUSY_BIT						7

//FIFO BLOCK DEFINES
#define DAQ0804_FIFO_BLOCK_OFFSET					0x40
#define DAQ0804_FIFO_THRESHOLD_LSB_REG				DAQ0804_FIFO_BLOCK_OFFSET + 0		
#define DAQ0804_FIFO_THRESHOLD_MSB_REG				DAQ0804_FIFO_BLOCK_OFFSET + 1	
#define DAQ0804_FIFO_DEPTH_LSB_REG					DAQ0804_FIFO_BLOCK_OFFSET + 4		
#define DAQ0804_FIFO_DEPTH_MSB_REG					DAQ0804_FIFO_BLOCK_OFFSET + 5
#define DAQ0804_FIFO_FIFOENABLE_REG					DAQ0804_FIFO_BLOCK_OFFSET + 0x0C
#define DAQ0804_FIFO_FLAGS_REG						DAQ0804_FIFO_BLOCK_OFFSET + 0x0D	
#define DAQ0804_FIFO_RESET_OFFSET					DAQ0804_FIFO_BLOCK_OFFSET + 0x0D

////////////////////////
// DIO BLOCK DEFINES
////////////////////////
#define DAQ0804_DIO_BLOCK_OFFSET				0x20
#define DAQ0804_DIO_A_DIR_REG_OFFSET			DAQ0804_DIO_BLOCK_OFFSET+0x08
#define DAQ0804_DIO_B_DIR_REG_OFFSET			DAQ0804_DIO_BLOCK_OFFSET+0x09
#define DAQ0804_DIO_C_DIR_REG_OFFSET			DAQ0804_DIO_BLOCK_OFFSET+0x0A
#define DAQ0804_DIO_PORT_A						0
#define DAQ0804_DIO_PORT_B						1
#define DAQ0804_DIO_PORT_C						2

//////////////////////////////////////////////
// COUNTER BLOCK DEFINES- COUNTER/PWM/WDT
//////////////////////////////////////////////
#define DAQ0804_COUNTER_BLOCK_OFFSET			0x30
#define DAQ0804_COUNTER_DATA_BYTE0				DAQ0804_COUNTER_BLOCK_OFFSET+0
#define DAQ0804_COUNTER_DATA_BYTE1				DAQ0804_COUNTER_BLOCK_OFFSET+1
#define DAQ0804_COUNTER_DATA_BYTE2				DAQ0804_COUNTER_BLOCK_OFFSET+2
#define DAQ0804_COUNTER_DATA_BYTE3				DAQ0804_COUNTER_BLOCK_OFFSET+3
#define DAQ0804_COUNTER_NUMBER_REGISTER			DAQ0804_COUNTER_BLOCK_OFFSET+4
#define DAQ0804_COUNTER_CMD_REGISTER			DAQ0804_COUNTER_BLOCK_OFFSET+5

#define DAQ0804_COUNTER_CMD_CLEAR					0x00
#define DAQ0804_COUNTER_CMD_LOAD					0x10
#define DAQ0804_COUNTER_CMD_SEL_DIRECTION_DOWN		0x20
#define DAQ0804_COUNTER_CMD_SEL_DIRECTION_UP		0x21
#define DAQ0804_COUNTER_CMD_EXTGATE_DISABLE			0x30
#define DAQ0804_COUNTER_CMD_EXTGATE_ENABLE			0x31
#define DAQ0804_COUNTER_CMD_COUNTER_DISABLE			0x40
#define DAQ0804_COUNTER_CMD_COUNTER_ENABLE			0x41
#define DAQ0804_COUNTER_CMD_COUNTER_OUTPUT_ENABLE	0x80
#define DAQ0804_COUNTER_CMD_COUNTER_OUTPUT_DISABLE	0x80 //Both enable/disable commands upper bits are same
#define DAQ0804_COUNTER_CMD_COUNTER_LATCH			0x50
#define DAQ0804_COUNTER_CMD_RESET_ALL				0xF1
#define DAQ0804_COUNTER_CMD_RESET_ONE				0xF0
#define DAQ0804_COUNTER_CMD_CLKSELECT				0x60
#define DAQ0804_COUNTER_CMD_CLKSELECT_EXT			0x60
#define DAQ0804_COUNTER_CMD_CLKSELECT_50MHZ			0x62
#define DAQ0804_COUNTER_CMD_CLKSELECT_1MHZ			0x63
#define DAQ0804_COUNTER_DISABLE_OUTPUT              0x80
#define DAQ0804_COUNTER_AUTO_RELOAD_ENABLE          0x71
#define DAQ0804_COUNTER_AUTO_RELOAD_SET             0x70
#define DAQ0804_COUNTER_CLKSRC0_BIT					0
#define DAQ0804_COUNTER_CLKFRQ0_BIT					1
#define DAQ0804_COUNTER_COUNTER0					0
#define DAQ0804_COUNTER_COUNTER1					1
#define DAQ0804_COUNTER_CMD_OUTPULSE_WIDTH	    0x90

//DA Block Defines
#define DAQ0804_DA_BLOCK_OFFSET						0x10
#define DAQ0804_DACODE_LSB							DAQ0804_DA_BLOCK_OFFSET+0
#define DAQ0804_DACODE_MSB							DAQ0804_DA_BLOCK_OFFSET+1
#define DAQ0804_COMMAND_REG							DAQ0804_DA_BLOCK_OFFSET+4
#define DAQ0804_DARANGE_REG							DAQ0804_DA_BLOCK_OFFSET+5
#define DAQ0804_DASIM_REG							DAQ0804_DA_BLOCK_OFFSET+6
#define DAQ0804_NUMBER_OF_DA_CHANNEL				4
#define DAQ0804_DACOMMAND							DAQ0804_DA_BLOCK_OFFSET+7
#define DAQ0804_DABUSY_READ							DAQ0804_DA_BLOCK_OFFSET+7
#define DAQ0804_DASIMUP_VALUE						0x40
#define DAQ0804_READ_BIT_DACBUSY    				7
#define DAQ0804_DA_CMD_LOAD_DAC_INPUT_REG			0x10
#define DAQ0804_DADELAY_WRITE						14
#define DAQ0804_NUM_DA_CHANNELS					4

// PWM command masks
#define DAQ0804_PWM_BLOCK_OFFSET					0x30
#define DAQ0804_PWM_CMD_REG	   					DAQ0804_PWM_BLOCK_OFFSET+0xB
#define DAQ0804_PWM_DATA_LSB  						DAQ0804_PWM_BLOCK_OFFSET+0x08
#define DAQ0804_PWM_DATA_CSB  						DAQ0804_PWM_BLOCK_OFFSET+0x09
#define DAQ0804_PWM_DATA_MSB  						DAQ0804_PWM_BLOCK_OFFSET+0x0A
#define DAQ0804_PWM_LOAD_C0_COUNTER					0x10
#define DAQ0804_PWM_LOAD_C1_COUNTER					0x18
#define DAQ0804_PWM_POLARITY_HIGH					0x20
#define DAQ0804_PWM_POLARITY_LOW					0x28
#define DAQ0804_PWM_DISABLE_PULSE_OUTPUT			0x30
#define DAQ0804_PWM_ENABLE_PULSE_OUTPUT				0x38
#define DAQ0804_PWM_STOP_CURRENT_PWM 				0x08
#define DAQ0804_PWM_STOP_ALL_PWMS					0x00
#define DAQ0804_PWM_DISABLE_OUTPUT_ON_DIO_PORT_F	0x50
#define DAQ0804_PWM_ENABLE_OUTPUT_ON_DIO_PORT_F		0x58
#define DAQ0804_PWM_SELECT_50MHZ_CLOCK_SOURCE		0x60
#define DAQ0804_PWM_SELECT_1MHZ_CLOCK_SOURCE		0x68
#define DAQ0804_PWM_START_CURRENT_PWM				0x70
#define DAQ0804_PWM_START_ALL_PWMS					0x7F
#define DAQ0804_PWM_SELECTED_MASK					0x07
#define DAQ0804_PWM_COUNTING_PERIOD_MAX				16777215.0
#define DAQ0804_COUNTER_50MHZ						50000000
#define DAQ0804_COUNTER_1MHZ  						1000000
#define DAQ0804_PWM_POLARITY_HIGH					0x20
#define DAQ0804_PWM_POLARITY_LOW					0x28
#define DAQ0804_PWM_ENABLE             				0x38
#define DAQ0804_PWM_START              				0x70
#define DAQ0804_MAX_PWM						   		 04
#define DAQ0804_PWM_STOP_SELECTED_PWM  				0x08
#define DAQ0804_PWM_STOP_ALL_PWM				0x00
#define DAQ0804_PWM_CLEAR_SELECTED_PWM				0x40
#define DAQ0804_PWM_CLEAR_ALL_PWM				0x48
	
#define	DSC_VENDORID								0x4453//0x1C0E
#define DAQ0804_DEVICEID							0x0C00

/////////////////////////
// D/A WAVEFORM GENERATOR DEFINES
/////////////////////////
#define DAQ0804_DA_BLOCK_OFFSET						0x10
#define DAQ0804_WRITE_WGCMD							DAQ0804_DA_BLOCK_OFFSET+0x0B
#define DAQ0804_WRITE_WGCFG							DAQ0804_DA_BLOCK_OFFSET+0x0A

#define DAQ0804_READ_WGCFG							DAQ0804_DA_BLOCK_OFFSET+0x0A
#define DAQ0804_READ_WGCMD							DAQ0804_DA_BLOCK_OFFSET+0x0B

#define DAQ0804_WRITE_WGLSB							DAQ0804_DA_BLOCK_OFFSET+0x08
#define DAQ0804_WRITE_WGMSB							DAQ0804_DA_BLOCK_OFFSET+0x09

#define DAQ0804_WGCYCLE_BIT_POSITION				7

#define DAQ0804_FRAME_COUNT_LSB_REGISTER			DAQ0804_DA_BLOCK_OFFSET+0x0C
#define DAQ0804_FRAME_COUNT_MSB_REGISTER			DAQ0804_DA_BLOCK_OFFSET+0x0D

#define DAQ0804_READ_BIT_OVF			3
#define DAQ0804_READ_BIT_CLKFRQ0		1
#define DAQ0804_READ_BIT_CLKFRQ1		6

#define DAQ0804_WRITE_BIT_CT0LOAD		0
#define DAQ0804_WRITE_BIT_CT1LOAD		0
#define DAQ0804_WRITE_BIT_CT0LATCH		1
#define DAQ0804_WRITE_BIT_CT1LATCH		1


//#define DAQ0804_MAX_DACS		  4
#define DAQ0804_MAX_DA_CHANNELS   4
#define DAQ0804_BIT_DAWAIT        7

/////////////////////////
// MISC DEFINES
/////////////////////////

#define DAQ0804_BITS_IN_BYTE_MAX  7   // maximum bit indices in a byte (0-7)
#define DAQ0804_UNSIGNED_BYTE_MAX 255 // maximum value of an unsigned byte
#define DAQ0804_BIT_LOW           0   // 0 represents a bit setting of low
#define DAQ0804_BIT_HIGH	      1   // 1 represents a bit setting of high
#define DAQ0804_BOARD_RESET       0
#define DAQ0804_FPGA_RESET        1
#define DAQ0804_AD_RESET          2
#define DAQ0804_FIFO_RESET        3
#define DAQ0804_DA_RESET          4



/////////////////////////
//  STRUCTS
/////////////////////////

typedef struct
{
	int		Range;			//0-1; 0 = 5V, 1 = 10V
	int 	Polarity;		//0-1; 0 = bipolar, 1 = unipolar
	int 	Sedi;			//0-1; 0 = single-ended, 1 = differential
	int 	Sign;			//0-1; in Diff mode only: 0 = even channel is high; 1 = odd channel is high
	int		 Lowch	;		//low channel, 0-7 for SE mode or 0-3 for Diff mode
	int 	Highch;			//high channel, 0-7 for SE mode or 0-3 for Diff mode
	int 	ADClock	;		//0-3: 0 = command bit ADSTART = 1; 1 = falling edge of DIO bit 19; 2 = rising edge 
							//of output of counter 0; 3 = rising edge of output of counter 1
	int 	ScanEnable;		//0 = disable, 1 = enable scan mode
	int 	ScanInterval;	//0 = 10us, 1 = 12.5us, 2 = 20us, 3 = programmable; used only if ScanEnable  = 1
	int 	ProgInt	;		//100-255, used only if ScanInterval = 3; interval is this value times 100ns

}DAQ0804ADSETTINGS;

typedef struct
{

	int				FIFOEnable;			//0 = disable; interrupt occurs after each sample / scan; 1 = enable; interrupt
										//occurs on FIFO threshold flag
	int 			FIFOThreshold;		//0-2048, indicates level at which FIFO will generate an interrupt if FIFOEnable = 1
	int 			Cycle	;			//0 = one shot operation, interrupts will stop when the selected no. of 
										//samples / scans are acquired; 1 = continuous operation until terminated
	int 			NumConversions;		//if Cycle = 0 this is the number of samples / scans to acquire; if Cycle = 1 
										//this is the size of the circular buffer in samples / scans
	SWORD *ADBuffer;			//pointer to A/D buffer to hold the samples; the buffer must be greater than or 
										//equal to NumConversions x 1 if scan is disabled or NumConversions x Scansize if 
										//scan is enabled (Scansize is Highch \96 Lowch + 1)
}DAQ0804ADINT;

typedef struct
{

	int 	OpStatus;			//0 = not running, 1 = running
	int 	NumConversions;		//Number of conversions since interrupts started
	int 	Cycle;				//0 = one-shot operation, 1 = continuous operation
	int 	FIFODepth;			//Current FIFO depth pointer
	int 	BufferPtr;			//Position in A/D storage buffer, used in continuous mode when buffer is being
								//repetitively overwritten
	int 	OF;					//0 = no overflow, 1 = FIFO overflow (attempt to write to FIFO when FIFO was full)
	int 	FF;					//0 = FIFO not full, 1 = FIFO is full
	int 	TF;					//0 = number of A/D samples in FIFO is less than the programmed threshold, 1 = number 
								//of A/D samples in FIFO is equal to or greater than the programmed threshold
	int 	EF;					//0 = FIFO has unread data in it, 1 = FIFO is empty

}DAQ0804ADINTSTATUS;

typedef struct
{

	int 			CtrNo;		//Counter number, 0-7
	unsigned long 	CtrData	;	//Initial load data, 32-bit straight binary
	int 			CtrCmd;		//Counter command, 0-15 (see FPGA specification for available commands)
	int 			CtrClk;		//Clock source, must be 2 or 3 (see FPGA specification for usage)
	int 			CtrOutEn;	//1 = enable output onto corresponding I/O pin; 0 = disable output
	int 			CtrOutPol;	//1 = output pulses high, 0 = output pulses low; only used if CtrOutEn = 1
	int 			CtrCountDir;//1=Up direction and 0-Down direction
	float			Rate;		// Desired output rate, Hz
	int 			CtrReload	;	//0 = one-shot counting, 1 = auto-reload (repetitive counting, only works in count down mode)
	int 			CtrCmdData	;	//Auxiliary data for counter command, 0-3 (see FPGA specification for usage)
	int 			ctrOutWidth ; // 0-3   0 = 1 clocks, 1 = 10 clocks, 2 = 100 clocks, 3 = 1000 clocks , only used if  CtrOutEn = 1 and CtrClock = 2 or 3
	
}DAQ0804COUNTER;

typedef struct
{

	int		Threshold;		//Current FIFO programmed threshold
	int 	Depth	;		//Current FIFO depth pointer
	int 	Enable;			//0 = FIFO is not currently enabled, 1 = FIFO is currently enabled
	int 	OF;				//0 = no overflow, 1 = FIFO overflow (attempt to write to FIFO when FIFO was full)
	int 	FF;				//0 = FIFO not full, 1 = FIFO is full
	int 	TF;				//0 = number of A/D samples in FIFO is less than the programmed threshold,
							//1 = number of A/D samples in FIFO is equal to or greater than the programmed threshold
	int 	EF;				//0 = FIFO has unread data in it, 1 = FIFO is empty


}DAQ0804FIFO;

typedef struct
{

	int	Enable;			//0 = disable interrupts, 1 = enable interrupts; if Enable = 0 then no other parameters are required
	void (*IntFunc) (void *parameter);	//pointer to user function to run when interrupts occur
	int 	Mode	;		//0 = alone, 1 = before standard function, 2 = after standard function
	int 	Source	;		//Selects interrupt source:	0 = A/D, 1 = unused, 2 = counter 2 output, 3 = counter 3 output, 4 = digital I/O
	int 	BitSelect;		//0-20 selects which DIO line to use to trigger interrupts; only used if Source = 4
	int 	Edge;			//1 = rising edge, 0 = falling edge; only used if Source = 4

}DAQ0804USERINT;

typedef struct
{

	unsigned int	*Waveform;		//pointer to array of 16-bit unsigned data; If multiple channels are being set up at the same time, the data must be previously interleaved by the program, i.e. ch. 0, ch. 1, ch. 2, ch. 0, ch. 1, ch. 2, \85; the array size must be equal to Frames x Framesize; the array size must be no greater than 2048
	int 			Frames	;		//total number of frames in the array
	int 			FrameSize;		//no. of channels to be driven = frame size
	int 			*Channels;		//List of channels to be driven by the waveform generator; the number of values in this array must be equal to Framesize; channels can be in any sequence
	int				Clock;			//0 = software increment; 1 = counter/timer 0 output; 2 = counter/timer 1 output; 3 = DIO pin D0
	float 			Rate	;		//frame update rate, Hz (only used if Clock = 1 or 2)
	int 			Cycle	;		//0 = one-shot operation; 1 = repetitive operation

}DAQ0804WAVEFORM;

typedef struct
{
		int Num;				/*PWM number, 0-3*/
		float Rate;				/*output frequency in Hz*/
		float Duty;				/*initial duty cycle, 0-100*/
		int Polarity;			/*0 = pulse high, 1 = pulse low*/
		int OutputEnable;		/*0 = disable output, 1 = enable output on DIO pin*/
		int Run	;				/*0 = don't start PWM, 1 = start PWM*/
		int Command;			/*0-15 = PWM command*/
		int CmdData;			/*0 or 1 for auxiliary PWM command data (used for certain commands)*/
		unsigned long Divisor;	/*24-bit value for use with period and duty cycle commands*/

}DAQ0804PWM;



/////////////////////////
// Function Prototypes //
/////////////////////////

BYTE DAQ0804Main(DSCB board, WORD func, void * params);
BYTE DSCUDAPICALL DAQ0804FreeBoard(DSCB board);
BYTE DSCUDAPICALL DAQ0804InitBoard(DSCCBP* dsccbp);
BYTE DSCUDAPICALL DAQ0804LED(BoardInfo* bi, int enable);

BYTE DSCUDAPICALL DAQ0804DIOConfig(BoardInfo* bi, int Bit, int Dir);
BYTE DSCUDAPICALL DAQ0804DIOConfigAll(BoardInfo* bi, int* Config);
BYTE DSCUDAPICALL DAQ0804DIOOutputByte(BoardInfo* bi, int Port, int Data);
BYTE DSCUDAPICALL DAQ0804DIOInputByte(BoardInfo* bi, int port, BYTE* data);
BYTE DSCUDAPICALL DAQ0804DIOOutputBit(BoardInfo* bi, int Bit, int Value);
BYTE DSCUDAPICALL DAQ0804DIOInputBit(BoardInfo* bi, int Bit, int* Value);
BYTE DSCUDAPICALL DAQ0804Config(BoardInfo* bi, int Value);

BYTE DSCUDAPICALL DAQ0804CounterSetRate(BoardInfo* bi, DAQ0804COUNTER *Ctr);
BYTE DSCUDAPICALL DAQ0804CounterConfig(BoardInfo* bi, DAQ0804COUNTER *Ctr);
BYTE DSCUDAPICALL DAQ0804CounterRead(BoardInfo* bi, int CtrNo, unsigned long * CtrData);
BYTE DSCUDAPICALL DAQ0804CounterReset(BoardInfo* bi, int CtrNum);
BYTE DSCUDAPICALL DAQ0804CounterFunction(BoardInfo* bi, DAQ0804COUNTER * Ctr);

BYTE DSCUDAPICALL DAQ0804PWMStart(BoardInfo* bi, int Num);
BYTE DSCUDAPICALL DAQ0804PWMConfig(BoardInfo* bi, DAQ0804PWM* DAQ0804pwm);
BYTE DSCUDAPICALL DAQ0804PWMStop(BoardInfo* bi, int Num);
BYTE DSCUDAPICALL DAQ0804PWMCommand(BoardInfo* bi, DAQ0804PWM* DAQ0804pwm);
BYTE DSCUDAPICALL DAQ0804PWMReset(BoardInfo* bi, int Num);

BYTE DSCUDAPICALL DAQ0804DASetSettings(BoardInfo* bi, int Range, int Sim);
BYTE DSCUDAPICALL DAQ0804DAConvert(BoardInfo* bi, int Channel, unsigned int DACode);
BYTE DSCUDAPICALL DAQ0804DAConvertScan(BoardInfo* bi, int* ChannelSelect, unsigned int* DACodes);
BYTE DSCUDAPICALL DAQ0804DAFunction(BoardInfo* bi, unsigned int DAData, int DACommand);
BYTE DSCUDAPICALL DAQ0804DAUpdate(BoardInfo* bi);

BYTE DSCUDAPICALL DAQ0804WaveformBufferLoad(BoardInfo* bi, DAQ0804WAVEFORM* DAQ0804waveform);
BYTE DSCUDAPICALL DAQ0804WaveformDataLoad(BoardInfo* bi, int Address, int Channel, unsigned Value);
BYTE DSCUDAPICALL DAQ0804WaveformConfig(BoardInfo* bi, DAQ0804WAVEFORM* DAQ0804waveform);
BYTE DSCUDAPICALL DAQ0804WaveformStart(BoardInfo* bi);
BYTE DSCUDAPICALL DAQ0804WaveformPause(BoardInfo* bi);
BYTE DSCUDAPICALL DAQ0804WaveformReset(BoardInfo* bi);
BYTE DSCUDAPICALL DAQ0804WaveformInc(BoardInfo* bi);

BYTE DSCUDAPICALL DAQ0804UserInterruptConfig(BoardInfo* bi, DAQ0804USERINT* DAQ0804userint);
BYTE DSCUDAPICALL DAQ0804UserInterruptRun(BoardInfo* bi, int Source, int Bit, int Edge);
BYTE DSCUDAPICALL DAQ0804UserInterruptCancel(BoardInfo* bi, int Source);

BYTE DSCUDAPICALL DAQ0804ADSetSettings(BoardInfo* bi, DAQ0804ADSETTINGS* settings);
BYTE DSCUDAPICALL DAQ0804ADSetTiming(BoardInfo* bi, DAQ0804ADSETTINGS* settings);
BYTE DSCUDAPICALL DAQ0804ADSetChannelRange(BoardInfo* bi, DAQ0804ADSETTINGS* settings);
BYTE DSCUDAPICALL DAQ0804ADSetChannel(BoardInfo* bi, int Channel);
BYTE DSCUDAPICALL DAQ0804ADTrigger(BoardInfo* bi, unsigned int* Sample);
BYTE DSCUDAPICALL DAQ0804ADConvert(BoardInfo* bi, DAQ0804ADSETTINGS* settings, unsigned* Sample);
BYTE DSCUDAPICALL DAQ0804FIFOStatus(BoardInfo* bi, DAQ0804FIFO* Fifo);
BYTE DSCUDAPICALL DAQ0804ADInt(BoardInfo* bi, DAQ0804ADINT* DAQ0804adint);
BYTE DSCUDAPICALL DAQ0804ADIntStatus(BoardInfo* bi, DAQ0804ADINTSTATUS* intstatus);
BYTE DSCUDAPICALL DAQ0804ADIntPause(BoardInfo* bi);
BYTE DSCUDAPICALL DAQ0804ADIntResume(BoardInfo* bi);
BYTE DSCUDAPICALL DAQ0804ADIntCancel(BoardInfo* bi);

BYTE DAQ0804InputLong ( BoardInfo* bi, DWORD start_address, DWORD* data );

#else //tells people that there's no DAQ0804

BYTE DAQ0804Main(DSCB board, WORD func, void * params);

#endif

#ifdef __cplusplus
} /* Closes the extern "C" */
#endif

#endif //#ifndef _DSC_DAQ0804_H


