#Cenarios
if {$argc == 3} {
    	set cenario [lindex $argv 0]
   	set protocolo [lindex $argv 1]
	set quebra [lindex $argv 2]
if {$cenario != 1 && $cenario != 2} {
    	puts "Apenas pode escolher entre cenario 1 e 2."
    	exit 1
}
if {$protocolo != "udp" && $protocolo != "tcp"} {
    	puts "Apenas pode escolher entre protocolo udp e tcp."
    	exit 1
}
if {$quebra != "sim" && $quebra != "nao"} {
    	puts "Apenas pode escolher entre sim ou nao."
    	exit 1
}
} else {
	puts "Apenas recebe um argumento(1 ou 2)"
    puts "ns projeto.tcl <cenario> <protocolo>"
    puts "cenario; 1 ou 2"
    puts "protocolo: udp ou tcp"
    puts "quebra: sim ou nao"
    exit 1
}

set ns [new Simulator]
$ns rtproto DV
set nf [open out.nam w]
$ns namtrace-all $nf
set nt [open out.tr w]
$ns trace-all $nt

proc fim {} { 
	global ns nf nt
	$ns flush-trace 
	close $nf
	close $nt
	exec nam out.nam 
	exit 0
}

#Servidor 1
set n0 [$ns node]
$n0 color red
$n0 shape hexagon
$n0 label "Servidor 1"
#Servidor 2
set n1 [$ns node]
$n1 color red
$n1 shape hexagon
$n1 label "Servidor 2"
#Receptor 1
set n2 [$ns node]
$n2 color blue
$n2 shape square
$n2 label-at down
$n2 label "Receptor 1"
#Receptor 2
set n3 [$ns node]
$n3 color blue
$n3 shape square
$n3 label-at down
$n3 label "Receptor 2"
#Router 4
set n4 [$ns node]
$n4 label "Router 4"
#Router 5
set n5 [$ns node]
$n5 label "Router 5"
#Router 6
set n6 [$ns node]
$n6 label "Router 6"

#Servidor 1 -> Router 4
$ns duplex-link $n0 $n4 50Mb 10ms DropTail
$ns queue-limit $n0 $n4 2098
$ns duplex-link-op $n0 $n4 queuePos 1.5
#Servidor 2 -> Router 5
$ns duplex-link $n1 $n5 0.1Gb 10ms DropTail
$ns duplex-link-op $n1 $n5 queuePos 1.5
#Router 4 -> Router 5
$ns duplex-link $n4 $n5 200Mb 10ms DropTail
#Router 4 -> Router 6
$ns duplex-link $n4 $n6 1Gb 10ms DropTail
#Router 5 -> Router 6
$ns duplex-link $n5 $n6 100Mb 10ms DropTail
#Router 6 -> Receptor 1
$ns duplex-link $n6 $n2 40Mb 3ms DropTail
$ns duplex-link-op $n6 $n2 queuePos 0.5
#Router 4 -> Receptor 2
$ns duplex-link $n4 $n3 10Mb 10ms DropTail
$ns duplex-link-op $n4 $n3 queuePos 1.5

#Disposicao dos nodes/ligacoes
$ns duplex-link-op $n0 $n4 orient down
$ns duplex-link-op $n4 $n3 orient down
$ns duplex-link-op $n4 $n6 orient right-down
$ns duplex-link-op $n4 $n5 orient right
$ns duplex-link-op $n6 $n5 orient up
$ns duplex-link-op $n5 $n1 orient up
$ns duplex-link-op $n6 $n2 orient right
#Cores
$ns color 1 Blue
$ns color 2 Red
$ns color 3 Green
set cbr0 [new Application/Traffic/CBR]
$cbr0 set packetSize_ 2097152

if {$protocolo == "udp"} {

	#Cria um agente UDP e liga-o ao nó n0
	set udp0 [new Agent/UDP]
	$ns attach-agent $n0 $udp0
	#Cria uma fonte de tráfego CBR e liga-a ao udp0
	$cbr0 set maxpkts_ 1
	$cbr0 attach-agent $udp0
	#Cria um agente Null e liga-o ao nó n2
	set null0 [new Agent/Null]
	$ns attach-agent $n2 $null0
	$ns connect $udp0 $null0

	#$ns rtmodel-at 0.6 down $n4 $n6
	#$ns rtmodel-at 0.7 up $n4 $n6

	$udp0 set class_ 1
	$ns at 0.5 "$cbr0 start"
	$ns at 1.5 "$cbr0 stop"

} else {
	set tcp0 [new Agent/TCP]
	$ns attach-agent $n0 $tcp0

	$cbr0 attach-agent $tcp0
	$tcp0 set window_ 20
	set sink0 [new Agent/TCPSink]
	$ns attach-agent $n2 $sink0
	$ns connect $tcp0 $sink0
	
	#$ns rtmodel-at 0.6 down $n4 $n6
	#$ns rtmodel-at 0.7 up $n4 $n6

	$tcp0 set class_ 1
	$ns at 0.5 "$cbr0 start"


}

if {$cenario == 2} {

	#Cria um agente UDP e liga-o ao nó n1
	set udp1 [new Agent/UDP]
	$ns attach-agent $n1 $udp1
	#Cria uma fonte de tráfego CBR e liga-a ao udp1
	set cbr1 [new Application/Traffic/CBR]
	$cbr1 set rate_ 3mb
	$cbr1 attach-agent $udp1
	#Cria um agente Null e liga-o ao nó n2
	set null1 [new Agent/Null]
	$ns attach-agent $n2 $null1
	$ns connect $udp1 $null1

	#Cria um agente UDP e liga-o ao nó n1
	set udp2 [new Agent/UDP]
	$ns attach-agent $n1 $udp2
	#Cria uma fonte de tráfego CBR e liga-a ao udp2
	set cbr2 [new Application/Traffic/CBR]
	$cbr2 set rate_ 3Mb
	$cbr2 attach-agent $udp2
	#Cria um agente Null e liga-o ao nó n2
	set null2 [new Agent/Null]
	$ns attach-agent $n3 $null2
	$ns connect $udp2 $null2


	$udp1 set class_ 2
	$udp2 set class_ 3
	$ns at 0.5 "$cbr1 start"
	$ns at 5.5 "$cbr1 stop"
	$ns at 0.5 "$cbr2 start"
	$ns at 5.5 "$cbr2 stop"
}
if {$quebra == "sim"} {
	$ns rtmodel-at 0.6 down $n4 $n6
	$ns rtmodel-at 0.7 up $n4 $n6
}

$ns at 6.0 "fim"

$ns run
