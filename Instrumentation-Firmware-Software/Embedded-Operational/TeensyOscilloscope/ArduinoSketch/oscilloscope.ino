#define BUFFER_SIZE 480
static volatile uint16_t sinetable[BUFFER_SIZE];


void DACInit() {
  
  // fill up the sine table
  for(int i=0; i<BUFFER_SIZE; i++) {
    sinetable[i] = 2048+(int)(2048*sin(((float)i)*20.0*6.28318530717958647692/((float)BUFFER_SIZE)));
  }
  // initialise the DAC
  SIM_SCGC2 |= SIM_SCGC2_DAC0; // enable DAC clock
  DAC0_C0 = DAC_C0_DACEN | DAC_C0_DACRFS; // enable the DAC module, 3.3V reference
  // slowly ramp up to DC voltage
  for (int16_t i=0; i<2048; i+=1) {
    *(int16_t *)&(DAC0_DAT0L) = i;
    delayMicroseconds(125); // this function may be broken
  }
  // fill up the buffer with 2048
  for (int16_t i=0; i<16; i+=1) {
    *(int16_t *)(&DAC0_DAT0L + 2*i) = 2048;//256*(16-i) - 1;
  }
  // initialise the DMA
  // first, we need to init the dma and dma mux
  // to do this, we enable the clock to DMA and DMA MUX using the system timing registers
  SIM_SCGC6 |= SIM_SCGC6_DMAMUX; // enable DMA MUX clock
  SIM_SCGC7 |= SIM_SCGC7_DMA;    // enable DMA clock
  // next up, the channel in the DMA MUX needs to be configured
  DMAMUX0_CHCFG0 |= DMAMUX_SOURCE_DAC0; //Select DAC as request source
  DMAMUX0_CHCFG0 |= DMAMUX_ENABLE;      //Enable DMA channel 0
  // then, we enable requests on our channel
  DMA_ERQ = DMA_ERQ_ERQ0; // Enable requests on DMA channel 0
  // first, we need to init the dma and dma mux
  // to do this, we enable the clock to DMA and DMA MUX using the system timing registers
  SIM_SCGC6 |= SIM_SCGC6_DMAMUX; // enable DMA MUX clock
  SIM_SCGC7 |= SIM_SCGC7_DMA;    // enable DMA clock
  // next up, the channel in the DMA MUX needs to be configured
  DMAMUX0_CHCFG0 |= DMAMUX_SOURCE_DAC0; //Select DAC as request source
  DMAMUX0_CHCFG0 |= DMAMUX_ENABLE;      //Enable DMA channel 0
  // then, we enable requests on our channel
  DMA_ERQ = DMA_ERQ_ERQ0; // Enable requests on DMA channel 0
  // Here we choose where our data is coming from, and where it is going
  DMA_TCD0_SADDR = sinetable;   // set the address of the first byte in our LUT as the source address
  DMA_TCD0_DADDR = &DAC0_DAT0L; // set the first data register as the destination address
  // now we need to set the read and write offsets - kind of boring
  DMA_TCD0_SOFF = 4; // advance 32 bits, or 4 bytes per read
  DMA_TCD0_DOFF = 4; // advance 32 bits, or 4 bytes per write
  // this is the fun part! Now we get to set the data transfer size...
  DMA_TCD0_ATTR  = DMA_TCD_ATTR_SSIZE(DMA_TCD_ATTR_SIZE_32BIT);
  DMA_TCD0_ATTR |= DMA_TCD_ATTR_DSIZE(DMA_TCD_ATTR_SIZE_32BIT) | DMA_TCD_ATTR_DMOD(31 - __builtin_clz(32)); // set the data transfer size to 32 bit for both the source and the destination
  // ...and the number of bytes to be transferred per request (or 'minor loop')...
  DMA_TCD0_NBYTES_MLNO = 16; // we want to fill half of the DAC buffer, which is 16 words in total, so we need 8 words - or 16 bytes - per transfer
  // set the number of minor loops (requests) in a major loop
  // the circularity of the buffer is handled by the modulus functionality in the TCD attributes
  DMA_TCD0_CITER_ELINKNO = DMA_TCD_CITER_ELINKYES_CITER(BUFFER_SIZE*2/16);
  DMA_TCD0_BITER_ELINKNO = DMA_TCD_BITER_ELINKYES_BITER(BUFFER_SIZE*2/16);
  // the address is adjusted by these values when a major loop completes
  // we don't need this for the destination, because the circularity of the buffer is already handled
  DMA_TCD0_SLAST    = -BUFFER_SIZE*2;
  DMA_TCD0_DLASTSGA = 0;
  // do the final init of the channel
  DMA_TCD0_CSR = 0;
  // enable DAC DMA
  DAC0_C0 |= DAC_C0_DACBBIEN | DAC_C0_DACBWIEN; // enable read pointer bottom and waterwark interrupt
  DAC0_C1 |= DAC_C1_DMAEN | DAC_C1_DACBFEN | DAC_C1_DACBFWM(3); // enable dma and buffer
  DAC0_C2 |= DAC_C2_DACBFRP(0);
  // init the PDB for DAC interval generation
  SIM_SCGC6 |= SIM_SCGC6_PDB; // turn on the PDB clock  
  PDB0_SC |= PDB_SC_PDBEN; // enable the PDB  
  PDB0_SC |= PDB_SC_TRGSEL(15); // trigger the PDB on software start (SWTRIG)  
  PDB0_SC |= PDB_SC_CONT; // run in continuous mode  
  PDB0_MOD = 20-1; // modulus time for the PDB  
  PDB0_DACINT0 = (uint16_t)(20-1); // we won't subdivide the clock... 
  PDB0_DACINTC0 |= 0x01; // enable the DAC interval trigger  
  PDB0_SC |= PDB_SC_LDOK; // update pdb registers  
  PDB0_SC |= PDB_SC_SWTRIG; // ...and start the PDB

  
}



void setup() {

  Serial.begin(9600);
  while (!Serial) {
    yield();
  }

  DACInit();
  
}
void loop() {
  int sensorValue = analogRead(A0);
  Serial.println(sensorValue);
  // do nothing
}
