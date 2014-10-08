# floorpaint-server

The server for floorpaint.

## Level format

    $SIZE:START_LOCATION:SPECIAL_BLOCKS$

Examples:

    $4x4:4:0b,1b,14b,15b$

Block specifiers (any single character that matches `[^0-9,:$]`)

*   `b`: a block
*   `k`: a kitten
