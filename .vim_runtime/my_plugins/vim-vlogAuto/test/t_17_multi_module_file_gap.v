// +FHDR------------------------------------------------------------
//                 Copyright (c) 2024 JoinSilicon.
//                       ALL RIGHTS RESERVED
// -----------------------------------------------------------------
// Filename      : t_17_multi_module_file_gap.v
// Description   : Multi-module file - known gap. New impl only processes
//                 the first module; second module's /*autodefine*/ is
//                 ignored. This test documents the gap.
// -----------------------------------------------------------------
// -FHDR------------------------------------------------------------

module mod_a(/*AUTOARG*/
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

wire                            undecl_a;
test_sub u_a(/*autoinst*/
         .x          ( undecl_a      )
);
endmodule

module mod_b(/*AUTOARG*/
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

wire                            undecl_b;
test_sub u_b(/*autoinst*/
         .x          ( undecl_b      )
);
endmodule

//verilog-library-files: ()
//verilog-library-directories: (".")