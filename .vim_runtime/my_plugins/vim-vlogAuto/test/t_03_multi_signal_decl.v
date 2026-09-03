// +FHDR------------------------------------------------------------
//                 Copyright (c) 2024 JoinSilicon.
//                       ALL RIGHTS RESERVED
// -----------------------------------------------------------------
// Filename      : t_03_multi_signal_decl.v
// Description   : Multi-signal declaration in one line: wire a, b, c;
// -----------------------------------------------------------------
// -FHDR------------------------------------------------------------

module t_03_multi_signal_decl(/*AUTOARG*/
    //Inouts
    clk, data_out
);

//---------------------------
//ports {{{
//---------------------------
input                           clk;
output [7:0]                    data_out;
//}}}

//---------------------------
//wires && regs
//---------------------------
/*autodefine*/

wire a, b, c;
reg  [3:0] r1, r2;

test_sub u_sub(/*autoinst*/
         .clk        ( clk           )
        ,.x          ( undecl_x      )
        ,.y          ( undecl_y      )
);

endmodule

//verilog-library-files: ()
//verilog-library-directories: (".")