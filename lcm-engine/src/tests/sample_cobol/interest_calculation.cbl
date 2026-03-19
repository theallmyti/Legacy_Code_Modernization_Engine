       IDENTIFICATION DIVISION.
       PROGRAM-ID. INTEREST-CALCULATION.
       ENVIRONMENT DIVISION.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WS-PRINCIPAL      PIC 9(7)V99 VALUE 10000.00.
       01  WS-RATE           PIC 9(2)V99 VALUE 05.00.
       01  WS-TIME           PIC 9(2)    VALUE 03.
       01  WS-INTEREST       PIC 9(7)V99.
       01  WS-TOTAL-AMOUNT   PIC 9(7)V99.
       
       PROCEDURE DIVISION.
       MAIN-LOGIC.
           COMPUTE WS-INTEREST = (WS-PRINCIPAL * WS-RATE * WS-TIME) / 100
           COMPUTE WS-TOTAL-AMOUNT = WS-PRINCIPAL + WS-INTEREST
           
           DISPLAY "Principal: $" WS-PRINCIPAL
           DISPLAY "Rate: " WS-RATE "%"
           DISPLAY "Time: " WS-TIME " years"
           DISPLAY "Simple Interest: $" WS-INTEREST
           DISPLAY "Total Amount: $" WS-TOTAL-AMOUNT
           
           STOP RUN.
