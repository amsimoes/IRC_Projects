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

#for {set i 0} {$i < 6} {incr i} {
#	set n($i) [$ns node]
#}

set n0 [$ns node]
set n1 [$ns node]
set n2 [$ns node]
set n3 [$ns node]
set n4 [$ns node]
set n5 [$ns node]

$ns duplex-link $n0 $n1 20Kb 1.45ms DropTail
$ns duplex-link $n2 $n3 2Mb 8ms DropTail
$ns duplex-link $n4 $n5 20Mb 67ms DropTail

#Cria um agente UDP e liga-o ao nó n(0)
set udp0 [new Agent/UDP]
$ns attach-agent $n0 $udp0
set udp1 [new Agent/UDP]
$ns attach-agent $n2 $udp1
set udp2 [new Agent/UDP]
$ns attach-agent $n4 $udp2

#Cria uma fonte de tráfego CBR e liga-a ao udp0
set cbr0 [new Application/Traffic/CBR]
$cbr0 set packetSize_ 500
$cbr0 set maxpkts_ 1
$cbr0 attach-agent $udp0

set cbr1 [new Application/Traffic/CBR]
$cbr1 set packetSize_ 500
$cbr1 set maxpkts_ 1
$cbr1 attach-agent $udp1

set cbr2 [new Application/Traffic/CBR]
$cbr2 set packetSize_ 500
$cbr2 set maxpkts_ 1
$cbr2 attach-agent $udp2

#Cria um agente Null e liga-o ao nó n(3)
set null0 [new Agent/Null]
$ns attach-agent $n1 $null0
set null1 [new Agent/Null]
$ns attach-agent $n3 $null1
set null2 [new Agent/Null]
$ns attach-agent $n5 $null2

$ns connect $udp0 $null0
$ns connect $udp1 $null1
$ns connect $udp2 $null2

$ns at 0.5 "$cbr0 start"
$ns at 0.5 "$cbr1 start"
$ns at 0.5 "$cbr2 start"
$ns at 8.5 "$cbr0 stop"
$ns at 8.5 "$cbr1 stop"
$ns at 8.5 "$cbr2 stop"


$ns at 9.0 "fim"
$ns run 