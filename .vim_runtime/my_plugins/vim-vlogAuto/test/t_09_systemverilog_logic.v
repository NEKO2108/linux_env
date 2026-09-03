// +FHDR------------------------------------------------------------
//                 Copyright (c) 2024 JoinSilicon.
//                       ALL RIGHTS RESERVED
// -----------------------------------------------------------------
// Filename      : t_09_systemverilog_logic.v
// Description   : SystemVerilog logic / always_ff / always_comb
// -----------------------------------------------------------------
// -FHDR------------------------------------------------------------

module t_09_systemverilog_logic(/*AUTOARG*/
    //Inouts
    clk, data_in, data_out
);

//---------------------------
//ports {{{
//---------------------------
input  logic                    clk;
input  logic [7:0]              data_in;
output logic [7:0]              data_out;
//}}}

//---------------------------
//wires && regs
//---------------------------
/*autodefine*/

always_ff @(posedge clk) begin
    undecl_reg <= data_in;
end

always_comb begin
    undecl_l = data_out;
end

endmodule

//verilog-library-files: ()
//verilog-library-directories: (".")