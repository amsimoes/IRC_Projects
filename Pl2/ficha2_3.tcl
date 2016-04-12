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

$ns duplex-link $n0 $n1 1Mb 10ms DropTail
$ns duplex-link $n2 $n3 1Mb 10ms DropTail

#$ns duplex-link-op $n0 $n1 orient right
#$ns duplex-link-op $n2 $n3 orient right

#cria um agente udp e liga-o ao no n0
set udp0 [new Agent/UDP]
$ns attach-agent $n0 $udp0

#cria uma fonte de trafego cbr e liga-a ao udp0 // packetSize_ em BYTES
set cbr0 [new Application/Traffic/CBR]
$cbr0 set packetSize_ 2
$cbr0 set interval_ 2
$cbr0 set maxpkts_ 10
$cbr0 attach-agent $udp0

#cria um agente udp e liga-o ao no n2
set udp1 [new Agent/UDP]
$ns attach-agent $n2 $udp1

#cria uma fonte de trafego cbr e liga-a ao udp1
set cbr1 [new Application/Traffic/CBR]
$cbr1 set packetSize_ 16
$cbr1 set interval_ 1
$cbr1 set maxpkts_ 1
$cbr1 attach-agent $udp1

#cria um agente null e liga-o ao no n1
set null0 [new Agent/Null]
$ns attach-agent $n1 $null0

#cria um agente null e liga-o ao no n3
set null1 [new Agent/Null]
$ns attach-agent $n3 $null1

$ns connect $udp0 $null0
$ns connect $udp1 $null1

$ns at 0.3 "$cbr0 start"
$ns at 22.0 "$cbr0 stop"
$ns at 0.6 "$cbr1 start"
$ns at 22.0 "$cbr1 stop"

$ns at 23.5 "fim"

$ns run