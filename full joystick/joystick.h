#include "stm32f4xx_hal.h"

extern UART_HandleTypeDef huart10;

// Proccesing data from joystick and send it to PSD
void Uart_Transmit_Joystick_Data(uint16_t* adc_data);
