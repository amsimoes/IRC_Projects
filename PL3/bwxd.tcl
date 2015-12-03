# TCP Sliding Window
#
#

if {$argc == 4} {
    set bandwidth [lindex $argv 0]
    set delay [lindex $argv 1]
    set window [lindex $argv 2]
    set time [lindex $argv 3]
} else {
    puts "            bandwidth"
    puts "     n0 --------------- n1"
    puts " TCP_window    delay"
    puts "Usage: $argv0 bandwidth delay window simulation_time"
    exit 1
}

# Create the 'Simulator' object
set ns [new Simulator]

# Open a file for writing the nam trace data
set nf [open out.nam w]

$ns namtrace-all $nf

# Add a 'finish' procedure that closes the trace and starts nam
proc finish {} {
    global ns nf
    $ns flush-trace
    close $nf
    exec nam out.nam &
    exit 0
}

$ns color 1 Red
$ns color 2 Blue
$ns color 1 Green

# Define the topology
set n0 [$ns node]
set n1 [$ns node]

#   object      from  to  bandwith   delay    queue
$ns duplex-link $n0   $n1 $bandwidth $delay   DropTail
$ns duplex-link-op $n0   $n1 orient left-right

# Create a traffic source in node n0
set tcp [$ns create-connection TCP/RFC793edu $n0 TCPSink $n1 1]
$tcp set window_ $window
$tcp set packetSize_ 500

set ftp [new Application/FTP]
$ftp attach-agent $tcp

# When to start and to stop sending

$ns at 0.0 "$ftp start"
$ns at $time "finish"

####### END OF USER CODE ####################################################
#############################################################################

# Start the simulation
$ns run

