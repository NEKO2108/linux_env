// +FHDR------------------------------------------------------------
//                 Copyright (c) 2024 JoinSilicon.
//                       ALL RIGHTS RESERVED
// -----------------------------------------------------------------
// Filename      : t_12_manual_decl_no_recreate.v
// Description   : manual decls (wire/reg/inout) must NOT be re-created
// -----------------------------------------------------------------
// -FHDR------------------------------------------------------------

module t_12_manual_decl_no_recreate(/*AUTOARG*/
    //Inouts
    clk, data_in, data_out, manual_inout
);

//---------------------------
//ports {{{
//---------------------------
input                           clk;
input  [7:0]                    data_in;
output [7:0]                    data_out;
inout  [7:0]                    manual_inout;
//}}}

//---------------------------
//wires && regs
//---------------------------
/*autodefine*/

// Manually declared wires - should NOT be re-created
wire                            manual_wire;
wire [7:0]                      manual_bus;

// Manually declared regs - should NOT be re-created
reg  [7:0]                      manual_reg;

// Multi-signal declaration - all should NOT be re-created
reg  [7:0]                      manual_multireg_a, manual_multireg_b;

// Reg with initial value
reg                             manual_init_reg = 1'b0;

always @(posedge clk) begin
    manual_reg        <= data_in;
    manual_multireg_a <= data_in;
    manual_multireg_b <= manual_multireg_a;
    manual_init_reg   <= 1'b1;
    undecl_reg        <= data_in;
end

test_sub u_sub(/*autoinst*/
         .clk        ( clk           )
        ,.in         ( manual_wire   )
        ,.bus        ( manual_bus    )
        ,.inout_pin  ( manual_inout  )
        ,.out        ( undecl_out    )
);

endmodule

//verilog-library-files: ()
//verilog-library-directories: (".")