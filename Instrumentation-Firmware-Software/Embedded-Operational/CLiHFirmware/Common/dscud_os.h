/*

	DSCUD_OS.H
	
	Diamond Systems Corporation Universal Driver
	Version 7 

	(c) Diamond Systems Corporation 2010
	
	http://www.diamondsystems.com

	(c) Copyright 2010 Diamond Systems Corporation. Use of this source code
	is subject to the terms of Diamond Systems' Software License Agreement.
	Diamond Systems provides no warranty of proper performance if this
	source code is modified.
*/


#ifndef _DSCDSCUD_OS_H
#define _DSCDSCUD_OS_H

////////////////////////////
// DSCUD Internal Defines //
////////////////////////////
//#ifdef DSC_FPDAQ1616_SUPPORT
//   #define NUM_INT_TYPES 10  // Added INT_TYPE_COUNTER0 and INT_TYPE_COUNTER1
//#else
   #define NUM_INT_TYPES 8
//#endif

#define MAX_BOARDS   16   // Max number of boards you can control with the driver

#define DSC_PCI_VENDOR_ID 0x11db   /* Temporary development ID */
/* #define DSC_PCI_VENDOR_ID 0x10de */        /* National Semiconductor */

// Maximum number of DIO ports that can be configured to have
// an interrupt-driven latched operation
#define NUM_INT_DRIVEN_LATCH_DIOPORTS 4

///////////////////////////////
// DSCUD Internal Structures //
///////////////////////////////

//define a type for function pointer to DOS interrupt service routines
typedef void (*func_ptr_ISR) (void* pData);

//define a type for function pointer to standard board call
typedef BYTE (*func_ptr_stnd) (void* bi);

//define a type for function pointer to board's interrupt start and end
typedef BYTE (*func_ptr_ints) (void* bi, DWORD int_type);

//define a type for function pointer to board's channel setter
typedef BYTE (*func_ptr_chan) (void* bi, BYTE low_channel, BYTE high_channel);

#if defined(WDE) && defined(USE_SHARED_BUFFERS)
typedef enum
{
	TRANSFER_TYPE_NONE,
	TRANSFER_TYPE_READ,
	TRANSFER_TYPE_WRITE,
	TRANSFER_TYPE_USER,
} TRANSFER_TYPE;
#endif // WDE && USE_SHARED_BUFFERS

/////////////////////////////////////////////////////
//
// IntInfo
//
// Contains information pertaining to each interrupt
//
/////////////////////////////////////////////////////

typedef struct 
{
	BOOL internal_clock; //if TRUE, operation will use internal clock
	BOOL external_trigger; //if TRUE, use the external trigger
	BYTE low_channel; //low channel to perform op on
	BYTE high_channel; //high channel to perform op on
	BOOL fifo_enab; //if TRUE, will use on-board FIFO (if available)
	BOOL scan_enab; //if TRUE, will use scan mode
	BOOL cycle_enab; //if TRUE, will recycle to beginning of buffer and loop
	DWORD max_transfers; //the max number of samples to take before cycling/ending
	DWORD cur_transfers; //the current number of samples taken
  	DWORD total_transfers; //the total number of transfers during the whole operation
  	DWORD prev_transfers; //the last cur_transfers value (for total_transfers stuff)
	BYTE flipflop_offset; //register offset from base for interrupt flip/flop
	BYTE fifo_reset;	// register offset from base for fifo reset
	BYTE fifo_overflow;  // register offset from base for fifo overflow
	BYTE ovf_bit;		// register bit on scale 0-7 for fifo overflow
	WORD* pSampleBuf; //pointer to the beginning of the sample buffer
	DWORD dump_threshold; //threshold at which to dump the sample buffer from kernel plugin
	WORD fifo_depth; //fifo depth to use
	BOOL int_chan_align; //if TRUE, an interrupt in cycle mode will call it's chan_func each cycle
	DSCUserInterruptFunction user_int; //user interrupt function pointer (NULL is no user interrupt)
	BYTE user_int_mode; // user int mode (USER_INT_AFTER/INSTEAD)
	BYTE channel_count;
	BYTE cur_channel;     
	BYTE int_enable_mask; //the bit mask for the register that determines interrupt operation status
	BYTE int_enable_reg; //base + this = which register to modify the above mask
	BYTE ready_for_int_disable;  // flag prevents multiple attempts to cancel interrupt threads
	DWORD overflows; // number of fifo overflows
	WORD* pCurPos; //pointer to the current position in the buffer
	DWORD int_type_ex;
	int Intclr ; // For EMM-DIO-4M board

#if defined(WDE) && defined(USE_SHARED_BUFFERS)
	void* /*PDATA_QUEUE_CONTEXT*/ pDataQueueContext;

	// X number of chunks are created when the board is initialized.
	// We want to keep half of the chunks for user and the other half
	// for the kernel to prevent underflow or overflow situations.
	// Since the interrupt info is not specified yet, it is possible
	// that num of chunks and dump_threshold are not aligned.
	// Therefore we will generate transfer events either when 
	// the dump_threshold is met or half of the chunks are filled/consumed.
	// This would be more efficient than an alternative solution of 
	// generating an event per FIFO transfer.
	// We will inform the app side only when the dump_threshold has been
	// reached as in the original algorithm.
	// The following parameter will keep the num of real transfers in between
	// 2 dump_threshold events. 
	// We will update the curr_transfers only when the dump_threshold condition meets.
	// By this way, we will keep the backward compatibility with the app side.
	DWORD realTransfers;

	// Num transfers over/under flowed.
	DWORD faultyTransfers;

	WORD* pCurPosWr;
#endif // WDE && USE_SHARED_BUFFERS

} IntInfo;

// Set in the BSL so the OSL can clear the DINT and latched status bit of the DIO port
typedef struct _DIOLatchInfo 
{
	BYTE latchOffset;
	BYTE latchBit;
	BYTE latchBitClear;
	BYTE latchBitClearOffset;
} DIOLatchInfo;

////////////
// BoardInfo
////////////

typedef struct
{
	BYTE active; //flag determining if board is alive
	BYTE lock; //flag determining if board is locked or not
	DSCCB dsccb; //the board's hardware settings structure
	DSCCBP dsccbp; //the PCI board's hardware settings structure
	DSCADSETTINGS dscadsettings; // keeps the settings such as gain, polarity, range... etc.

	BYTE portValues[18]; // stores the current byte value of each DIO port on the board
	WORD portValuesWord[18]; // stores the current word value of each 16 bit DIO port on the board
	BYTE Cregister; //used with the DMM16AT to remember counter registers
	BYTE revision; // used to check the revision of things.
	FLOAT rate_final;  //used to pass the true conversion rate between functions

	//////////////////////////////////////
	// For interrupt and DMA operations //
	//////////////////////////////////////
	BYTE op_type; //bitwise or of interrupt status.  Copied from int_type by dscGetStatus.
	DWORD int_type; //bitwise or of interrupt operation: INT_TYPE_AD, INT_TYPE_DA, INT_TYPE_DIO
	IntInfo int_info[NUM_INT_TYPES];

	func_ptr_stnd fifoReset_func; //function pointer to board's fifo reset
	func_ptr_ints start_func; //function pointer to board's interrupt start
	func_ptr_ints end_func; //function pointer to board's interrupt end
	func_ptr_chan chan_func; //function pointer to board's channel setter
	func_ptr_stnd oflow_func;
	
	
	// prior to this, there was no dscadsetscan function. This meant that
	// all the channel setting is in dscadscan which slows scan down
	// but for backwards compatibility you want to make sure that old code will
	// still run. So this is implemented. After a year from now we can delete it since
	// no customer will be running this. 5/01/02   - Kevin
	BYTE scan_channel_low; // the low channel of scan
	BYTE scan_channel_high; // the high channel of scan

	void* Modes; // stores a pointer to the proper DMM16AT Mode table (DMM16AT only).
	//BYTE enhanced_feature_enab;	//Currently for DMM32X, var true(1) if enhanced features enabled else false(0). 

	func_ptr_ISR newISR_func; //function pointer to board and function-specific ISR
	void* os_info; //pointer to os specific information
	
	BYTE interruptConf;

	// Set in BSL: 0 - Port A, 1 - Port B, 2 - Port C, 3 - Port D 
	// if other boards have more ports than four that can be configured 
	// to interrupt-driven DIO latched mode, then simply increase the size of the array
	DIOLatchInfo DIOLatchedInfo[NUM_INT_DRIVEN_LATCH_DIOPORTS]; 

	BYTE num_int_driven_latch_dioports; // Maximum number of interrupt-driven latched operational DIO ports to be set in BSL

} BoardInfo;

void DSCSleep(DWORD ms);
void DSCGetTime(DWORD* ms);
void DSCOutp(DWORD address, BYTE value);
void DSCOutpw(DWORD address, WORD value);
void DSCOutpl(DWORD address, DWORD value);
void DSCOutpws(DWORD address, WORD *buffer, WORD count);
BYTE DSCInp(DWORD address);
WORD DSCInpw(DWORD address);
DWORD DSCInpl(DWORD address);
void DSCInpws(DWORD address, WORD *buffer, WORD count);

BYTE DSCGetNumTransfers(BoardInfo * bi, DWORD int_index, DWORD * cur_transfer);
BYTE DSCGetDMM48ATOptoState(BoardInfo* bi, BYTE * state);
BYTE DSCEnableInt(BoardInfo* bi, DWORD int_type);
BYTE DSCDisableInt(BoardInfo* bi, DWORD int_type);
BYTE DSCSetSystemPriority(DWORD priority);

BYTE DSCInitDriverSubSys(DWORD version);
BYTE DSCFreeDriverSubSys(void);
BYTE DSCInitBoardSubSys(BoardInfo * bi);
BYTE DSCFreeBoardSubSys(BoardInfo * bi);
BYTE DSCPCIInitBoardSubSys(BoardInfo * bi);
BYTE DSCPCIFreeBoardSubSys(BoardInfo * bi);

/* Mutex functions for thread safety */
BYTE DSCBoardMutexLock(BoardInfo *bi);
BYTE DSCBoardMutexUnlock(BoardInfo *bi);
BYTE DSCGlobalMutexLock(void);
BYTE DSCGlobalMutexUnlock(void);

/* DON'T IMPLEMENT THESE FUNCTIONS */
BYTE DSCFlipFlopReset(BoardInfo* bi, DWORD int_type);
BYTE DSCSetLastError(BYTE error_code, const char* error_str);
BYTE DSCInitAllBoards(void);
BYTE DSCFreeAllBoards(void);
BYTE DSCWaitForBit(DWORD address, BYTE bit, BYTE targetvalue, DWORD ms);

#endif // #ifndef _DSCDSCUD_OS_H

