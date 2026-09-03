// +FHDR------------------------------------------------------------
//                 Copyright (c) 2024 JoinSilicon.
//                       ALL RIGHTS RESERVED
// -----------------------------------------------------------------
// Filename      : t_14_1995_explicit_port_decl.v
// Description   : 1995-style: port listed in header, typed in body.
//                 Explicit `wire clk;` should NOT be re-created.
// -----------------------------------------------------------------
// -FHDR------------------------------------------------------------

module t_14_1995_explicit_port_decl(/*AUTOARG*/
    //Inouts
    clk, din, dout
);

//---------------------------
//ports {{{
//---------------------------
input                           clk;
input  [7:0]                    din;
output [7:0]                    dout;
//}}}

//---------------------------
//wires && regs
//---------------------------
/*autodefine*/

wire                            clk;       // explicit decl of input port
wire [7:0]                      din;       // explicit decl of input port

test_sub u_sub(/*autoinst*/
         .clk        ( clk           )
        ,.in         ( din           )
        ,.out        ( undecl_out    )
);

endmodule

//verilog-library-files: ()
//verilog-library-directories: (".")