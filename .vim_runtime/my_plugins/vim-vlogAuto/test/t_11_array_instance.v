// +FHDR------------------------------------------------------------
//                 Copyright (c) 2024 JoinSilicon.
//                       ALL RIGHTS RESERVED
// -----------------------------------------------------------------
// Filename      : t_11_array_instance.v
// Description   : array instance u_sub[3:0] - undeclared output collected
// -----------------------------------------------------------------
// -FHDR------------------------------------------------------------

module t_11_array_instance(/*AUTOARG*/
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

test_sub u_sub[3:0] (/*autoinst*/
         .clk        ( clk           )
        ,.out        ( undecl_arr    )
);

endmodule

//verilog-library-files: ()
//verilog-library-directories: (".")