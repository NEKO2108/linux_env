// +FHDR------------------------------------------------------------
//                 Copyright (c) 2024 JoinSilicon.
//                       ALL RIGHTS RESERVED
// -----------------------------------------------------------------
// Filename      : t_18_short_marker.v
// Description   : /*autodef*/ short marker - now supported.
// -----------------------------------------------------------------
// -FHDR------------------------------------------------------------

module t_18_short_marker(/*AUTOARG*/
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
/*autodef*/

test_sub u_sub(/*autoinst*/
         .clk        ( clk           )
        ,.x          ( undecl_x      )
);

endmodule

//verilog-library-files: ()
//verilog-library-directories: (".")