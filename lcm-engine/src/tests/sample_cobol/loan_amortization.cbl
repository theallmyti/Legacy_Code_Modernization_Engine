       IDENTIFICATION DIVISION.
       PROGRAM-ID. LOAN-AMORTIZATION.
       ENVIRONMENT DIVISION.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WS-LOAN-AMOUNT    PIC 9(7)V99 VALUE 100000.00.
       01  WS-ANNUAL-RATE    PIC 9(2)V99 VALUE 06.00.
       01  WS-MONTHLY-RATE   PIC 9(2)V9(4).
       01  WS-YEARS          PIC 9(2)    VALUE 30.
       01  WS-MONTHS         PIC 9(3).
       01  WS-MONTHLY-PMT    PIC 9(7)V99.
       01  WS-TEMP1          PIC 9(9)V9(6).
       01  WS-TEMP2          PIC 9(9)V9(6).
       
       PROCEDURE DIVISION.
       MAIN-LOGIC.
           COMPUTE WS-MONTHS = WS-YEARS * 12
           COMPUTE WS-MONTHLY-RATE = (WS-ANNUAL-RATE / 100) / 12
           
           * Monthly Payment Formula: P * (r(1+r)^n) / ((1+r)^n - 1)
           COMPUTE WS-TEMP1 = WS-MONTHLY-RATE * ( (1 + WS-MONTHLY-RATE) ** WS-MONTHS )
           COMPUTE WS-TEMP2 = ( (1 + WS-MONTHLY-RATE) ** WS-MONTHS ) - 1
           COMPUTE WS-MONTHLY-PMT = WS-LOAN-AMOUNT * (WS-TEMP1 / WS-TEMP2)
           
           DISPLAY "Loan Amount: $" WS-LOAN-AMOUNT
           DISPLAY "Monthly Payment: $" WS-MONTHLY-PMT
           
           STOP RUN.
