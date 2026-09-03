// +FHDR------------------------------------------------------------
//                 Copyright (c) 2024 JoinSilicon.
//                       ALL RIGHTS RESERVED
// -----------------------------------------------------------------
// Filename      : t_19_no_marker.v
// Description   : No /*autodefine*/ marker - should print friendly
//                 "No '/*autodefine*/' found!" and leave file unchanged.
// -----------------------------------------------------------------
// -FHDR------------------------------------------------------------

module t_19_no_marker(/*AUTOARG*/
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
wire                            enable;

test_sub u_sub(/*autoinst*/
         .clk        ( clk           )
        ,.x          ( undecl_x      )
);

endmodule

//verilog-library-files: ()
//verilog-library-directories: (".")