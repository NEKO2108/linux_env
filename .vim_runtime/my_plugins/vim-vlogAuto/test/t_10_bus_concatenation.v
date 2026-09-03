// +FHDR------------------------------------------------------------
//                 Copyright (c) 2024 JoinSilicon.
//                       ALL RIGHTS RESERVED
// -----------------------------------------------------------------
// Filename      : t_10_bus_concatenation.v
// Description   : bus concatenation in instance port - split into hi/lo
// -----------------------------------------------------------------
// -FHDR------------------------------------------------------------

module t_10_bus_concatenation(/*AUTOARG*/
    //Inouts
    clk, data_out
);

//---------------------------
//ports {{{
//---------------------------
input                           clk;
output [15:0]                   data_out;
//}}}

//---------------------------
//wires && regs
//---------------------------
/*autodefine*/

test_sub u_sub(/*autoinst*/
         .clk        ( clk           )
        ,.in         ( {hi_byte, lo_byte} )
        ,.out        ( data_out      )
);

endmodule

//verilog-library-files: ()
//verilog-library-directories: (".")