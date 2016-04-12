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

for {set i 0} {$i < 4} {incr i} {
	set n($i) [$ns node]
}


$ns duplex-link $n(0) $n(1) 20Kb 2ms DropTail
$ns duplex-link $n(0) $n(2) 20Kb 2ms DropTail
$ns duplex-link $n(0) $n(3) 20Kb 2ms DropTail

#$ns duplex-link-op $n(2) $n(0) orient right-down
#$ns duplex-link-op $n(1) $n(0) orient right-up
#$ns duplex-link-op $n(1) $n(3) orient right-up
#$ns duplex-link-op $n(0) $n(3) orient right

set null0 [new Agent/Null]
$ns attach-agent $n(0) $null0

for {set i 1} {$i < 4} {incr i} {
	set udp($i) [new Agent/TCP]
	$ns attach-agent $n($i) $udp($i)
	$ns connect $udp($i) $null0
	
	set cbr($i) [new Application/Traffic/CBR]
	$cbr($i) attach-agent $udp($i)	
}

# (a) Sincrona, 4 em 4 ms, max 4995 + 2 syn + 2 fim
$cbr(1) set packetSize_ 4999
$cbr(1) set interval_ 0.004
$cbr(1) set maxpkts_ 1

# (b) Sincrona, 4 em 4 ms, 8 octetos de informação com 3 syn + 3 fim | 8 + 3 + 3 = 14
$cbr(2) set packetSize_ 14*8
$cbr(2) set interval_ 0.004
$cbr(2) set maxpkts_ 1

# (c) Assincrona, 2 em 2 ms, 8 bits + 2 start bits + 2 stop bits = 12 bits
$cbr(3) set packetSize_	12b 
$cbr(3) set interval_ 0.002
$cbr(3) set maxpkts_ 15


$ns at 0.1 "$cbr(1) start"
$ns at 0.3 "$cbr(2) start"
$ns at 0.6 "$cbr(3) start"
$ns at 1.0 "$cbr(1) stop"
$ns at 1.5 "$cbr(2) stop"
$ns at 2.0 "$cbr(3) stop"


$ns at 3.0 "fim"

$ns run