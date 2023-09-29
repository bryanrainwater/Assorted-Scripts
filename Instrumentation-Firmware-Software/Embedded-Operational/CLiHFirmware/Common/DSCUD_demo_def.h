/*

	DSCUD_demo_def.h
	
	Diamond Systems Corporation Universal Driver
	Version 7.00

	(c) Diamond Systems Corporation 2014
	
	http://www.diamondsystems.com

	(c) Copyright 2014 Diamond Systems Corporation. Use of this source code
	is subject to the terms of Diamond Systems' Software License Agreement.
	Diamond Systems provides no warranty of proper performance if this
	source code is modified.
*/


#ifndef DSCUD_DEMO_DEF_H
#define DSCUD_DEMO_DEF_H

#include <stdio.h>
#include <stdarg.h>
#include <string.h>


//Windows Header Files
#ifdef _WIN32
#ifndef _WIN32_WCE
#include <conio.h>
#endif

#include <windows.h>
#include <stdlib.h>
#include <math.h>
#define snprintf _snprintf
#define strncasecmp _strnicmp
#define strcasecmp _stricmp

// diamond driver includes
#include "dscud.h"
#endif


#ifdef _WIN32_WCE

#include <string.h>
#include <Winsock2.h>

//Windows CE Keyboard Function, since the OS does not have inbuilt kbhit()
static int kbhit()
{
	int i;
	int result = 0;

	result |= GetAsyncKeyState(VK_RETURN);
	result |= GetAsyncKeyState(VK_SPACE);

	if( result != 0)
	{
		 getchar();
		return 1;
	}

	// Capital character keys, A-Z
	for(i = 65; i <= 90; i++ )
		result |= GetAsyncKeyState(i);

	if( result != 0 )
	{
		getchar();
		return 1;
	}

	return result;
}

#endif
#include <time.h>

// DOS
#ifdef __BORLANDC__
#include <conio.h>
#include <dos.h>
#include <stdlib.h>
#include <math.h>
#include <mem.h>
// diamond driver includes
#include "dscud.h"
#endif

// Linux and QNX
#if defined(linux) || defined(__QNXNTO__) || defined(_WRS_VXWORKS_5_X)
#include <stdlib.h>
#include <math.h>
#include <time.h>
#include <termios.h>
#include <fcntl.h>
#include <unistd.h>
// diamond driver includes
#include "dscud.h"



//The following code section is for getch() function in Linux, since the OS does not have inbuilt getch()
static struct termios old, new;

/* Initialize new terminal i/o settings */
void initTermios(int echo) 
{
  tcgetattr(0, &old); /* grab old terminal i/o settings */
  new = old; /* make new settings same as old settings */
  new.c_lflag &= ~ICANON; /* disable buffered i/o */
  new.c_lflag &= echo ? ECHO : ~ECHO; /* set echo mode */
  tcsetattr(0, TCSANOW, &new); /* use these new terminal i/o settings now */
}

/* Restore old terminal i/o settings */
void resetTermios(void) 
{
  tcsetattr(0, TCSANOW, &old);
}

/* Read 1 character - echo defines echo mode */
char getch_(int echo) 
{
  char ch;
  initTermios(echo);
  ch = getchar();
  resetTermios();
  return ch;
}

/* Read 1 character without echo */
char getch(void) 
{
  return getch_(0);
}

/* Read 1 character with echo */
char getche(void) 
{
  return getch_(1);
}


#ifdef _WRS_VXWORKS_5_X
#include <selectLib.h>
#define main FPGPIO96DSCDIOFunctions
#else
#include <sys/time.h>
#endif
//Linux Keyboard Function, since the OS does not have inbuilt kbhit()
static int kbhit(void)
{
  struct termios oldt, newt;
  int ch;
  int oldf;
 
  tcgetattr(STDIN_FILENO, &oldt);
  newt = oldt;
  newt.c_lflag &= ~(ICANON | ECHO);
  tcsetattr(STDIN_FILENO, TCSANOW, &newt);
  oldf = fcntl(STDIN_FILENO, F_GETFL, 0);
  fcntl(STDIN_FILENO, F_SETFL, oldf | O_NONBLOCK);
 
  ch = getchar();
 
  tcsetattr(STDIN_FILENO, TCSANOW, &oldt);
  fcntl(STDIN_FILENO, F_SETFL, oldf);
 
  if(ch != EOF)
  {
    ungetc(ch, stdin);
    return 1;
  }
 
  return 0;
}
#endif
#include "dscud_os.h" 
#endif // #ifndef DSCUD_DEMO_DEF_H
