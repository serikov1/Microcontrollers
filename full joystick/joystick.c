#include "joystick.h"
 
uint8_t to_send1[12] = {0xA0, 0x0F, 0, 0, 0, 0, 0, 0, 0xA0, 0x0F, 0, 0};
uint8_t to_send2[12] = {0xB8, 0x0B, 0, 0, 0, 0, 0, 0, 0xB8, 0x0B, 0, 0};
uint8_t to_send3[12] = {0, 0, 0, 0, 0xA0, 0x0F, 0, 0, 0xA0, 0x0F, 0, 0};
uint8_t to_send4[12] = {0, 0, 0, 0, 0xB8, 0x0B, 0, 0, 0xB8, 0x0B, 0, 0};
void Uart_Transmit_Joystick_Data(uint16_t* adc_data)
 {
		 // x position left
		if(adc_data[1] > 4080 && adc_data[0] > 10 && adc_data[0] < 4080)
		{
			HAL_UART_Transmit_IT(&huart10, to_send1, 12);
		}
		//x position right
		if(adc_data[1] < 10 && adc_data[0] > 10 && adc_data[0] < 4080)
		{
			HAL_UART_Transmit_IT(&huart10, to_send3, 12);
		}
		// y position up
		if(adc_data[0] < 10 && adc_data[1] > 10 && adc_data[1] < 4080)
		{
			HAL_UART_Transmit_IT(&huart10, to_send2, 12);
		}
		//y position down
		if(adc_data[0] > 4080 && adc_data[1] > 10 && adc_data[1] < 4080)
		{
			HAL_UART_Transmit_IT(&huart10, to_send4, 12);
		}
 }
