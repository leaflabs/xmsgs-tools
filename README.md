
                                        _              _     
    __  ___ __ ___  ___  __ _ ___      | |_ ___   ___ | |___ 
    \ \/ / '_ ` _ \/ __|/ _` / __|_____| __/ _ \ / _ \| / __|
     >  <| | | | | \__ \ (_| \__ \_____| || (_) | (_) | \__ \
    /_/\_\_| |_| |_|___/\__, |___/      \__\___/ \___/|_|___/
                        |___/                                

Little python helpers for parsing through Xilinx build outputs.

### Install

This is pure python, no dependancies. Only tested on linux (debian wheezy).

Using pypi:

    pip install xmsgs-tools

Or, locally,

    python setup.py install

### Usage

Do ``xmsgsprint -h`` or ``xmsgsdiff -h`` for usage. Examples:

    bnewbold@ent$ xmsgsprint test/run_a/xst.xmsgs -t severe -f
    HDLCompiler:413: Result of 32-bit expression is truncated to fit in 2-bit target.
    HDLCompiler:413: Result of 32-bit expression is truncated to fit in 4-bit target.
    HDLCompiler:413: Result of 9-bit expression is truncated to fit in 8-bit target.
    HDLCompiler:413: Result of 9-bit expression is truncated to fit in 8-bit target.
    HDLCompiler:413: Result of 9-bit expression is truncated to fit in 8-bit target.
    HDLCompiler:413: Result of 3-bit expression is truncated to fit in 2-bit target.
    HDLCompiler:413: Result of 9-bit expression is truncated to fit in 8-bit target.
    HDLCompiler:413: Result of 32-bit expression is truncated to fit in 2-bit target.
    HDLCompiler:413: Result of 3-bit expression is truncated to fit in 2-bit target.
    HDLCompiler:413: Result of 32-bit expression is truncated to fit in 9-bit target.
    HDLCompiler:413: Result of 32-bit expression is truncated to fit in 12-bit target.
    HDLCompiler:413: Result of 32-bit expression is truncated to fit in 4-bit target.
    HDLCompiler:413: Result of 32-bit expression is truncated to fit in 5-bit target.

    === Summary ==================================================================
        Severe Warnings: 13


    bnewbold@ent$ xmsgsdiff test/run_a test/run_b --by-file -i 2261 2677 37 647 -s "*main*" -t warning
    --- <unknown>
    +Xst:0: Value "<PROCESSOR name={system} numA9Cores={2} clockFreq={666.66666...
    +Xst:2254: Area constraint could not be met for block <main>, final ratio i...

    === Summary ==================================================================
                Warnings: 153 (+2, -0)

### Example Raw .xmsgs

    <msg type="warning" file="Xst" num="37" delta="new" >Detected unknown constraint/property &quot;<arg fmt="%s" index="1">x_interface_info</arg>&quot;. This constraint/property is not supported by the current software release and will be ignored.
    </msg>

    <msg type="info" file="Xst" num="3210" delta="new" >&quot;<arg fmt="%s" index="1">/home/bnewbold/leaf/twl/dds/hdl/block_design/ip/block_design_axi_gpio_0_0/synth/block_design_axi_gpio_0_0.vhd</arg>&quot; line <arg fmt="%s" index="2">167</arg>: Output port &lt;<arg fmt="%s" index="3">gpio_io_o</arg>&gt; of the instance &lt;<arg fmt="%s" index="4">U0</arg>&gt; is unconnected or connected to loadless signal.
    </msg>

### Notes

'fulltext' is not a unique identifier; many warning texts are repeated

See also, XReport GUI tool.

### TODO

- Are message numbers unique across tools? If not, need more sophisticated filtering.
- Collapse redundant warnings (eg, every bit on on the same port)
