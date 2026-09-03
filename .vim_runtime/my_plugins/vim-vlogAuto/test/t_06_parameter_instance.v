// +FHDR------------------------------------------------------------
//                 Copyright (c) 2024 JoinSilicon.
//                       ALL RIGHTS RESERVED
// -----------------------------------------------------------------
// Filename      : t_06_parameter_instance.v
// Description   : parameterized instance - #(.W(X)) skipped, .out collected
// -----------------------------------------------------------------
// -FHDR------------------------------------------------------------

module t_06_parameter_instance(/*AUTOARG*/
    //Inouts
    clk, data_out
);

//-/////////////////////////////////////////////////////////////////////////////////
//-//   Parameter Definition
//-/////////////////////////////////////////////////////////////////////////////////
parameter   WIDTH = 8;
localparam  DEPTH = 16;

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

test_sub #(
    .WIDTH(WIDTH),
    .DEPTH(undecl_depth)
) u_sub(/*autoinst*/
         .clk        ( clk           )
        ,.out        ( undecl_out    )
);

endmodule

//verilog-library-files: ()
//verilog-library-directories: (".")