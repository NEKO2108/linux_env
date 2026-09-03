// +FHDR------------------------------------------------------------
//                 Copyright (c) 2024 JoinSilicon.
//                       ALL RIGHTS RESERVED
// -----------------------------------------------------------------
// Filename      : t_02_1995_style_ports.v
// Description   : 1995-style port list with body-side decl (classic form)
// -----------------------------------------------------------------
// -FHDR------------------------------------------------------------

module t_02_1995_style_ports(/*AUTOARG*/
    //Inouts
    clk, rst_n, data_in, data_out
);

//---------------------------
//ports {{{
//---------------------------
input                           clk;
input                           rst_n;
input  [7:0]                    data_in;
output [7:0]                    data_out;
//}}}

//---------------------------
//wires && regs
//---------------------------
/*autodefine*/

test_sub u_sub(/*autoinst*/
         .clk        ( clk           )
        ,.data_in    ( internal_data )
        ,.data_out   ( data_out      )
);

endmodule

//verilog-library-files: ()
//verilog-library-directories: (".")