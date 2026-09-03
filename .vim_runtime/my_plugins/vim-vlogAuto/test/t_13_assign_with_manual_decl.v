// +FHDR------------------------------------------------------------
//                 Copyright (c) 2024 JoinSilicon.
//                       ALL RIGHTS RESERVED
// -----------------------------------------------------------------
// Filename      : t_13_assign_with_manual_decl.v
// Description   : manual_wire declared+assigned -> not re-created;
//                 undecl_wire only assigned -> auto-created
// -----------------------------------------------------------------
// -FHDR------------------------------------------------------------

module t_13_assign_with_manual_decl(/*AUTOARG*/
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

wire                            manual_wire;

assign manual_wire = clk;       // declared + assigned: no re-create
assign undecl_wire = clk;       // not declared: should be auto-created

test_sub u_sub(/*autoinst*/
         .clk        ( clk           )
        ,.in         ( manual_wire   )
        ,.out        ( undecl_wire   )
);

endmodule

//verilog-library-files: ()
//verilog-library-directories: (".")