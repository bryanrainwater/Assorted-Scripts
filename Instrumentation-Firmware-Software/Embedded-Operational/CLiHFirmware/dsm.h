#ifndef CLIH_INTERFACE_H
#define CLIH_INTERFACE_H

#endif // CLIH_INTERFACE_H

/* Interface functions */

int initialize(int bufferSize, float waveFrequency, int laserNum, int numDAWaveChannels, int numADWaveChannels, int *scanBuffer);

void userfun();
void MPEuserfun();
int DMMuserfun();
int readBuffer(int *voltage);//, bool onlyReturnCount );
int statusMPE(void);
void MPEreadBuffer(int *voltage);
void writeMPEvoltage( float voltage , int channel);
int interface_close(void);
int analogIntStatus(void);//int lastCount );
void analogConvert(float *voltage);
void MPEanalogConvert(float *voltage);
int readBufferVoltage( float *voltage );
