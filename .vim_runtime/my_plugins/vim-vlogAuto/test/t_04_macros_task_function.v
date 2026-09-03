// +FHDR------------------------------------------------------------
//                 Copyright (c) 2024 JoinSilicon.
//                       ALL RIGHTS RESERVED
// -----------------------------------------------------------------
// Filename      : t_04_macros_task_function.v
// Description   : macros + task/function bodies must be skipped
// -----------------------------------------------------------------
// -FHDR------------------------------------------------------------

`define WIDTH 8

module t_04_macros_task_function(/*AUTOARG*/
    //Inouts
    clk, rst_n, data_in, data_out
);

//---------------------------
//ports {{{
//---------------------------
input                           clk;
input                           rst_n;
input  [`WIDTH-1:0]             data_in;
output [`WIDTH-1:0]             data_out;
//}}}

//---------------------------
//wires && regs
//---------------------------
/*autodefine*/

// wire comment;       -> ignored as comment
wire                            enable;
reg  [15:0]                     counter;
wire [`WIDTH-1:0]               internal_data;

// task should be skipped (its internal reg not collected)
task my_task;
    input [3:0] t_in;
    reg [3:0] t_reg;
begin
    t_reg = t_in;
end
endtask

test_sub u_sub(/*autoinst*/
         .clk        ( clk           )
        ,.data_in    ( internal_data )
        ,.out        ( undecl_out    )
);

endmodule

//verilog-library-files: ()
//verilog-library-directories: (".")