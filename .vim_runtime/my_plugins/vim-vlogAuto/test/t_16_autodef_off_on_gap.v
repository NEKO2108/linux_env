// +FHDR------------------------------------------------------------
//                 Copyright (c) 2024 JoinSilicon.
//                       ALL RIGHTS RESERVED
// -----------------------------------------------------------------
// Filename      : t_16_autodef_off_on_gap.v
// Description   : /*autodef off*/ ... /*autodef on*/ block - known gap.
//                 New impl does NOT recognize these markers; the test
//                 documents the current behavior.
// -----------------------------------------------------------------
// -FHDR------------------------------------------------------------

module t_16_autodef_off_on_gap(/*AUTOARG*/
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

wire                            enable;
/*autodef off*/
wire                            skip_me_pls;
reg                             skip_reg;
/*autodef on*/

test_sub u_sub(/*autoinst*/
         .clk        ( clk           )
        ,.x          ( undecl_x      )
);

endmodule

//verilog-library-files: ()
//verilog-library-directories: (".")