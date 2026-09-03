// +FHDR------------------------------------------------------------
//                 Copyright (c) 2024 JoinSilicon.
//                       ALL RIGHTS RESERVED
// -----------------------------------------------------------------
// Filename      : t_05_generate_block.v
// Description   : generate-for block must be skipped (inner wire not collected)
// -----------------------------------------------------------------
// -FHDR------------------------------------------------------------

module t_05_generate_block(/*AUTOARG*/
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

genvar i;
generate
    for (i=0; i<8; i=i+1) begin: gen_loop
        wire inner_wire;
        assign inner_wire = clk;
        test_sub u_sub_i (
            .clk(inner_wire),
            .in(gen_in_i)
        );
    end
endgenerate

test_top u_top(/*autoinst*/
         .x          ( undecl_top    )
);

endmodule

//verilog-library-files: ()
//verilog-library-directories: (".")