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
set n2 [$ns node]
set n3 [$ns node]

# A -> B || $n0 -> $n1
$ns duplex-link $n0 $n1 3Mb 5ms DropTail
# B -> C || $n1 -> $n2
$ns duplex-link $n1 $n2 1Gb 230ms DropTail
# C -> D || $n2 -> $n3
$ns duplex-link $n2 $n3 9.96Mb 0.05ms DropTail

$ns duplex-link-op $n0 $n1 orient right
$ns duplex-link-op $n1 $n2 orient right
$ns duplex-link-op $n2 $n3 orient right

set udp0 [new Agent/UDP]
$ns attach-agent $n0 $udp0

set cbr0 [new Application/Traffic/CBR]
$cbr0 set packetSize_ 20485
$cbr0 set interval_ 1
$cbr0 set maxpkts_ 1
$cbr0 attach-agent $udp0

set null [new Agent/Null]
$ns attach-agent $n3 $null

$ns connect $udp0 $null

$ns at 0.1 "$cbr0 start"


$ns at 2.5 "fim"
$ns run