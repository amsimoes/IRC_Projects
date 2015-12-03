set ns [new Simulator]

set nf [open out.nam w]
$ns namtrace-all $nf

proc fim {} {
        global ns nf
        $ns flush-trace
        close $nf
        exec nam out.nam
        exit 0
}

set n0 [$ns node]
set n1 [$ns node]

$ns at 5.0 "fim"
$ns run 
