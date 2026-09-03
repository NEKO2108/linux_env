// +FHDR------------------------------------------------------------
//                 Copyright (c) 2024 JoinSilicon.
//                       ALL RIGHTS RESERVED
// -----------------------------------------------------------------
// Filename      : t_07_ifdef_block.v
// Description   : `ifdef block - inside decls skipped (no macro def active)
// -----------------------------------------------------------------
// -FHDR------------------------------------------------------------

module t_07_ifdef_block(/*AUTOARG*/
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

`ifdef SIM
    wire sim_only_wire;
    reg  sim_only_reg;
`endif

test_sub u_sub(/*autoinst*/
         .clk        ( clk           )
        ,.sim        ( sim_only_wire )
);

endmodule

//verilog-library-files: ()
//verilog-library-directories: (".")