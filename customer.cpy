      *****************************************************************
      * EBCDIC to ASCII Converter Test Copybook                        *
      * This copybook contains examples of all supported data types    *
      *****************************************************************
       01  CUSTOMER-RECORD.
           05  CUSTOMER-ID                  PIC 9(6).
           05  CUSTOMER-NAME.
               10  LAST-NAME                PIC X(15).
               10  FIRST-NAME               PIC X(10).
               10  MIDDLE-INITIAL           PIC X.
           05  CUSTOMER-ADDRESS.
               10  STREET                   PIC X(25).
               10  CITY                     PIC X(15).
               10  STATE                    PIC XX.
               10  ZIP-CODE                 PIC X(10).
           05  CONTACT-INFO.
               10  PHONE-NUMBER             PIC X(12).
               10  EMAIL                    PIC X(30).
           05  ACCOUNT-INFO.
               10  ACCOUNT-NUMBER           PIC X(10).
               10  ACCOUNT-TYPE             PIC X.
                   88  CHECKING             VALUE 'C'.
                   88  SAVINGS              VALUE 'S'.
                   88  LOAN                 VALUE 'L'.
               10  ACCOUNT-BALANCE          PIC S9(9)V99 COMP-3.
               10  CREDIT-LIMIT             PIC S9(7)V99 COMP-3.
               10  INTEREST-RATE            PIC S9(3)V9(3) COMP-3.
           05  TRANSACTION-DATA.
               10  LAST-TRANSACTION-DATE.
                   15  YEAR                 PIC 9(4).
                   15  MONTH                PIC 9(2).
                   15  DAY                  PIC 9(2).
               10  LAST-TRANSACTION-AMOUNT  PIC S9(7)V99 COMP-3.
               10  TRANSACTION-COUNT        PIC 9(5) COMP.
           05  NUMERIC-TYPES-EXAMPLES.
               10  DISPLAY-NUMERIC          PIC 9(5).
               10  DISPLAY-NUMERIC-SIGNED   PIC S9(5).
               10  DISPLAY-DECIMAL          PIC 9(3)V99.
               10  DISPLAY-DECIMAL-SIGNED   PIC S9(3)V99.
               10  COMP-BINARY              PIC S9(4) COMP.
               10  COMP-3-PACKED            PIC S9(7)V99 COMP-3.
               10  COMP-1-FLOAT             COMP-1.
               10  COMP-2-DOUBLE            COMP-2.
               10  SIGN-SEPARATE-LEADING    PIC S9(5) SIGN LEADING SEPARATE.
               10  SIGN-SEPARATE-TRAILING   PIC S9(5) SIGN TRAILING SEPARATE.
               10  COMP-5-NATIVE            PIC S9(9) COMP-5.
               10  COMP-6-UNSIGNED          PIC 9(5) COMP-6.
           05  SPECIAL-FEATURES.
               10  JUSTIFIED-FIELD          PIC X(10) JUSTIFIED RIGHT.
               10  BLANK-WHEN-ZERO-FIELD    PIC 9(5) BLANK WHEN ZERO.
               10  FILLER                   PIC X(5).
               10  SYNCHRONIZED-FIELD       PIC S9(4) COMP SYNCHRONIZED.
           05  COMPLEX-STRUCTURES.
               10  OCCURS-EXAMPLE           OCCURS 5 TIMES.
                   15  ITEM-ID              PIC 9(3).
                   15  ITEM-NAME            PIC X(15).
                   15  ITEM-PRICE           PIC S9(5)V99 COMP-3.
               10  REDEFINES-EXAMPLE        PIC X(20).
               10  REDEFINES-ALTERNATIVE    REDEFINES REDEFINES-EXAMPLE.
                   15  ALT-CODE             PIC X(5).
                   15  ALT-DESCRIPTION      PIC X(15).
           05  FILLER                       PIC X(20).
