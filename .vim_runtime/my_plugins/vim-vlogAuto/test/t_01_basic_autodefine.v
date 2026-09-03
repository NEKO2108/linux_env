// +FHDR------------------------------------------------------------
//                 Copyright (c) 2024 JoinSilicon.
//                       ALL RIGHTS RESERVED
// -----------------------------------------------------------------
// Filename      : t_01_basic_autodefine.v
// Description   : Basic autodefine test (1995-style ports + AUTOARG)
// -----------------------------------------------------------------
// -FHDR------------------------------------------------------------

module t_01_basic_autodefine(/*AUTOARG*/
    //Inouts
    clk, rst_n, data_in, data_out, valid
);

//-/////////////////////////////////////////////////////////////////////////////////
//-//   Parameter Definition
//-/////////////////////////////////////////////////////////////////////////////////
parameter   DATA_WIDTH = 8;

//---------------------------
//ports {{{
//---------------------------
input                           clk;
input                           rst_n;
input  [DATA_WIDTH-1:0]         data_in;
output [DATA_WIDTH-1:0]         data_out;
output                          valid;
//}}}

//---------------------------
//wires && regs
//---------------------------
/*autodefine*/

test_sub u_sub(/*autoinst*/
         .clk        ( clk           )
        ,.data_in    ( internal_data )
        ,.data_out   ( data_out      )
        ,.valid      ( valid         )
);

endmodule

//verilog-library-files: ()
//verilog-library-directories: (".")