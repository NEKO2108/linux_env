// +FHDR------------------------------------------------------------
//                 Copyright (c) 2024 JoinSilicon.
//                       ALL RIGHTS RESERVED
// -----------------------------------------------------------------
// Filename      : t_20_long_names.v
// Description   : long signal names and long bit-width parameters
//                 should not truncate and should align correctly.
// -----------------------------------------------------------------
// -FHDR------------------------------------------------------------

module t_20_long_names(/*AUTOARG*/
    //Inouts
    clk, data_out
);

//-/////////////////////////////////////////////////////////////////////////////////
//-//   Parameter Definition
//-/////////////////////////////////////////////////////////////////////////////////
parameter   WIDTH_PARAM = 32;

//---------------------------
//ports {{{
//---------------------------
input                               clk;
output [WIDTH_PARAM-1:0]            data_out;
//}}}

//---------------------------
//wires && regs
//---------------------------
/*autodefine*/

test_sub u_sub(/*autoinst*/
         .clk        ( clk                              )
        ,.out        ( undecl_out_long_name_that_is_long )
);

endmodule

//verilog-library-files: ()
//verilog-library-directories: (".")