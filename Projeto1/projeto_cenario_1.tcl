if($argc == 3) {
	set cenario [lindex $argv 0]
	set quebra [lindex $argv 1]
	set prot [lindex $argv 2]
	if {$cenario != 1 && $cenario != 2} {
		puts "Escolha cenário 1 ou cenário 2"
		exit 1
	}
	if {$prot != "udp" && $prot != "tcp" && $prot != "UDP" && $prot != "TCP"} {
		puts "Escolha entre udp e tcp"
		exit 1
	}
	if {$quebra != 1 && $quebra != 0} {
		puts "Escolha 1 (Sim) ou 0 (Nao)"
		exit 1
	}
} else {
	puts "Cenário 1"
	puts "Para cenário 2: ns rate"
}

set ns [new Simulator]
$ns rtproto DV

set nf [open out.nam w]
$ns namtrace-all $nf

set nt [open out.tr w]
$ns trace-all $nt

proc fim {} {
	global ns nf
	$ns flush-trace
	close $nf
	exec nam out.nam
	exit 0
}

#Servidor 1
set n0 [$ns node]	
$n0 color red
$n0 shape hexagon
$n0 label-at left
$n0 label "Servidor 1"
$n0 label-color red
#Servidor 2
set n1 [$ns node]
$n1 color red
$n1 shape hexagon
$n1 label "Servidor 2"
$n1 label-color red
$n1 label-at right
# RECEPTOR 1
set n2 [$ns node]
$n2 color blue
$n2 label "Receptor 1"
$n2 label-color blue
# RECEPTOR 2
set n3 [$ns node]
$n3 color blue
$n3 label "Receptor 2"
$n3 label-color blue

# ROUTER 4
set n4 [$ns node]
# ROUTER 5
set n5 [$ns node]
# ROUTER 6
set n6 [$ns node]


$ns duplex-link $n0 $n4 50Mb 10ms DropTail
$ns duplex-link $n1 $n5 100Mb 10ms DropTail
$ns duplex-link $n4 $n5 200Mb 10ms DropTail
$ns duplex-link $n4 $n6 1Gb 10ms DropTail
$ns duplex-link $n5 $n6 100Mb 10ms DropTail
$ns duplex-link $n6 $n2 40Mb 3ms DropTail
$ns duplex-link $n4 $n3 10Mb 10ms DropTail

$ns duplex-link-op $n0 $n4 orient down
$ns duplex-link-op $n4 $n3 orient down
$ns duplex-link-op $n4 $n6 orient right-down
$ns duplex-link-op $n4 $n5 orient right
$ns duplex-link-op $n6 $n5 orient up
$ns duplex-link-op $n5 $n1 orient up
$ns duplex-link-op $n6 $n2 orient right

# SERVIDOR 1 -> TCP || SERVIDOR 2 -> UDP
# CENÁRIO 1 -> SERVIDOR 2 SEM TRÁFEGO
# CENÁRIO 2: SERVIDOR 2 -> RECEPTOR 1 e 2 = 3Mb/s

set cbr0 [new Application/Traffic/CBR]
$cbr0 set packetSize_ 2097152
$cbr0 set maxpkts_ 1

if {$prot == "udp" || $prot == "UDP"} {
	set udp0 [new Agent/UDP]
	$ns attach-agent $n0 $udp0
	$cbr0 attach-agent $udp0

	#Cria um agente Null e liga-o ao nó n2 (RECEPTOR 1)
	set null0 [new Agent/Null]
	$ns attach-agent $n2 $null0

	$ns connect $udp0 $null0
	$ns at 0.5 "$cbr0 start"
	#$ns at 4.0 "$cbr0 stop"
} else {	
	# Protocolo TCP

	#Cria um agente TCP e liga-o ao nó n0 (SERVIDOR 1)
	set tcp0 [new Agent/TCP]
	$ns attach-agent $n0 $tcp0
	$tcp0 set window_ 1000000
	$cbr0 attach-agent $tcp0

	#Criar agente Sink e ligar ao tcp0 - nó n2 (RECEPTOR 1)
	set sink0 [new Agent/TCPSink]
	$ns attach-agent $n2 $sink0
	$ns connect tcp0 sink0

	$tcp0 set class_ 1

	$ns at 0.5 "$cbr0 start"
}

# Cenário 2 -> SERVIDOR 2 ativo a emitir tráfego
if {$cen == 2} {
	#Criar um agente UDP para ligar ao SERVIDOR 2
	set udp1 [new Agent/UDP]
	$ns attach-agent $n1 $udp1

	set cbr1 [new Application/Traffic/CBR]
	$cbr1 set rate_ 3Mb
	$cbr1 attach-agent $udp1

	set null1 [new Agent/Null]
	$ns attach-agent $n2 $null1

	set udp2 [new Agent/UDP]
	$ns attach-agent $n1 $udp2

	set cbr2 [new Application/Traffic/CBR]
	$cbr2 set rate_ 3Mb
	$cbr2 attach-agent $udp2

	set null2 [new Agent/Null]
	$ns attach-agent $n3 $null2

	$udp1 set class_ 2
	$udp2 set class_ 3

	$ns connect $udp1 $null1
	$ns connect $udp2 $null2

	$ns at 0.5 "$cbr1 start"
	$ns at 0.5 "$cbr2 start"
	$ns at 4.0 "$cbr1 stop"
	$ns at 4.0 "$cbr2 stop"
}


set null0 [new Agent/Null]
$ns attach-agent $n2 $null0

$ns connect $udp0 $null0

$ns at 0.5 "$cbr0 start"




if {$quebra == 1} {
	$ns rtmodel-at 0.6 down $n4 $n6
	$ns rtmodel-at 0.7 up $n4 $n6
}


$ns at 5.0 "fim"
$ns run