#include "display.h"

void I2C_send(uint8_t data, uint8_t flags)
{
	HAL_StatusTypeDef res;
	    for(;;) {                                                                    
	        res = HAL_I2C_IsDeviceReady(&hi2c1, LCD_ADDR, 1, HAL_MAX_DELAY);       
	        if(res == HAL_OK) break;
	    }

	uint8_t up = data & 0xF0;
	uint8_t lo = (data << 4) & 0xF0;
	uint8_t data_arr[4];
	data_arr[0] = up|flags|BACKLIGHT|PIN_EN;
	data_arr[1] = up|flags|BACKLIGHT;
	data_arr[2] = lo|flags|BACKLIGHT|PIN_EN;
	data_arr[3] = lo|flags|BACKLIGHT;

	HAL_I2C_Master_Transmit(&hi2c1, LCD_ADDR, data_arr, sizeof(data_arr), HAL_MAX_DELAY);
	HAL_Delay(LCD_DELAY_MS);
}

void LCD_SendString(char *str)
{
	while(*str) {
		I2C_send((uint8_t)(*str), 1);
        str++;
    }
}

void Display_Init()
{
	I2C_send(0x30,0); //8bit interface
	I2C_send(0x2,0); // cursor to the beginning of the line
	I2C_send(0xC,0); // disable cursor
	I2C_send(0x1,0); // clean display
	LCD_SendString("   RC for PSD");
	I2C_send(0xC0,0); // move for next LCD line
	LCD_SendString("Powered by DASR");
}

uint16_t* Decompose_Int(uint16_t arr[6], uint16_t value1, uint16_t value2)
{
	int i = 0;
	while(value1 > 0)
		{
			arr[2 - i] = value1 % 10;
			value1 /= 10;
			i++;
		}
	int j = 0;
	while(value2 > 0)
		{
			arr[5 - j] = value2 % 10;
			value2 /= 10;
			j++;
		}
		return arr;
}

_Bool Check_Correctness_Recieved_Data(uint8_t* data)
{
	if((data[0] | data[1]<<8 | data[2]<<16 | data[3] << 24) + 
		(data[4] | data[5]<<8 | data[6]<<16 | data[7] << 24) == 
		(data[8] | data[9]<<8 | data[10]<<16 | data[11] << 24))
		{
			uint8_t to_send[12] = {0xE8, 0x03, 0, 0, 0, 0, 0, 0, 0xE8, 0x03, 0, 0};
			HAL_UART_Transmit_IT(&huart10, to_send, 12);
			return 1;
		}
	else
	{
		uint8_t to_send[12] = {0xD0, 0x07, 0, 0, 0, 0, 0, 0, 0xD0, 0x07, 0, 0};
		HAL_UART_Transmit_IT(&huart10, to_send, 12);
		return 0;
	}
}

void Send_Angles_To_Display(uint16_t* angles)
{
		uint16_t to_display_angles[6] = {0, 0, 0, 0, 0, 0};
		uint16_t azimuth = angles[0];
		uint16_t elevation = angles[1];
		Decompose_Int(to_display_angles, azimuth, elevation);
		LCD_SendString("Azimuth = ");
		I2C_send(to_display_angles[0] + 48, 1);
		I2C_send(to_display_angles[1] + 48, 1);
		I2C_send(to_display_angles[2] + 48, 1);
		I2C_send(0xC0,0); // move for next LCD line
		LCD_SendString("Elevation = ");
		I2C_send(to_display_angles[3] + 48, 1);
		I2C_send(to_display_angles[4] + 48, 1);
		I2C_send(to_display_angles[5] + 48, 1);
}


uint16_t elevation = 0;
uint16_t azimuth = 0;
uint16_t to_display[2] = {0, 0};
void Proccess_Data_and_View_To_Display(uint8_t* data)
{
	if((data[8] | data[9]<<8 | data[10]<<16 | data[11] << 24) == 
		 (data[0] | data[1]<<8 | data[2]<<16 | data[3] << 24) + 
		 (data[4] | data[5]<<8 | data[6]<<16 | data[7] << 24))
	{
		if((data[0] | data[1]<<8 | data[2]<<16 | data[3] << 24) == 0 && (data[4] | data[5]<<8 | data[6]<<16 | data[7] << 24) != 0)
		{
			elevation = (data[4] | data[5]<<8 | data[6]<<16 | data[7] << 24);
			to_display[1] =  elevation;
			to_display[0] = azimuth;
		}
		if((data[4] | data[5]<<8 | data[6]<<16 | data[7] << 24) == 0 && (data[0] | data[1]<<8 | data[2]<<16 | data[3] << 24) != 0)
		{
			azimuth = data[0] | data[1]<<8 | data[2]<<16 | data[3] << 24;
			to_display[0] = azimuth;
			to_display[1] = elevation;
		}
		if((data[4] | data[5]<<8 | data[6]<<16 | data[7] << 24) == 0 && (data[0] | data[1]<<8 | data[2]<<16 | data[3] << 24) == 0 && elevation != 0)
		{
			to_display[0] = azimuth;
			to_display[1] = elevation;
		}
	}
	Send_Angles_To_Display(to_display);
}
