// +FHDR------------------------------------------------------------
//                 Copyright (c) 2024 JoinSilicon.
//                       ALL RIGHTS RESERVED
// -----------------------------------------------------------------
// Filename      : t_15_idempotency_rerun.v
// Description   : re-running :AD on already-expanded module should
//                 replace (not duplicate) the auto block.
// -----------------------------------------------------------------
// -FHDR------------------------------------------------------------

module t_15_idempotency_rerun(/*AUTOARG*/
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
//auto wires{{{
wire       undecl_out;
//}}}
// End of automatic define

wire                            manual_wire;

test_sub u_sub(/*autoinst*/
         .clk        ( clk           )
        ,.in         ( manual_wire   )
        ,.out        ( undecl_out    )
);

endmodule

//verilog-library-files: ()
//verilog-library-directories: (".")