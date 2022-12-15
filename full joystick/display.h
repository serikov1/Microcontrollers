#include "stm32f4xx_hal.h"
#define LCD_ADDR (0x27 << 1)
#define PIN_RS (1 << 0)
#define PIN_EN (1 << 2)
#define BACKLIGHT (1 << 3)
#define LCD_DELAY_MS 5

extern I2C_HandleTypeDef hi2c1;
extern UART_HandleTypeDef huart10;

// Send settings to display
void I2C_send(uint8_t data, uint8_t flags);
// Send message to display
void LCD_SendString(char *str);
// Beginning settings for display
void Display_Init();
// Decompose int to array
uint16_t* Decompose_Int(uint16_t arr[6], uint16_t value1, uint16_t value2);
// Check for brokenness data
_Bool Check_Correctness_Recieved_Data(uint8_t* data);
// Send recieved angles to display
void Send_Angles_To_Display(uint16_t* angles);
// Preparing data from stm and send it using previous function
void Proccess_Data_and_View_To_Display(uint8_t* data);
