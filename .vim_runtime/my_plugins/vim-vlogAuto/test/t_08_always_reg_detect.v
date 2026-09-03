// +FHDR------------------------------------------------------------
//                 Copyright (c) 2024 JoinSilicon.
//                       ALL RIGHTS RESERVED
// -----------------------------------------------------------------
// Filename      : t_08_always_reg_detect.v
// Description   : always-block reg inference + assign wire inference
// -----------------------------------------------------------------
// -FHDR------------------------------------------------------------

module t_08_always_reg_detect(/*AUTOARG*/
    //Inouts
    clk, data_in, data_out
);

//---------------------------
//ports {{{
//---------------------------
input                           clk;
input  [7:0]                    data_in;
output [7:0]                    data_out;
//}}}

//---------------------------
//wires && regs
//---------------------------
/*autodefine*/

always @(posedge clk) begin
    undecl_reg  <= data_in;
    counter     <= counter + 1;
end

assign data_out = undecl_wire;

endmodule

//verilog-library-files: ()
//verilog-library-directories: (".")