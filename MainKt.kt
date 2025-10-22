package org.example

import org.eclipse.paho.client.mqttv3.*
import org.jline.terminal.TerminalBuilder

const val BROKER_ADDRESS = "tcp://192.168.4.1:1883"  // broker address
const val MQTT_PORT = 1883
const val TOPIC = "VR_control"

lateinit var client: MqttClient

// --- Cross-platform key input using JLine ---
fun get_key(): String {
    val terminal = TerminalBuilder.terminal()
    val reader = terminal.reader()
    val ch = reader.read().toChar()
    return ch.toString()
}

// --- MQTT callbacks ---

fun on_connect(reconnect: Boolean, serverURI: String?) {
    if (!reconnect) {
        println("✅ Connected to broker: $BROKER_ADDRESS")
    } else {
        println("♻️ Reconnected to broker: $BROKER_ADDRESS")
    }
    client.subscribe(TOPIC) { topic, message ->
        on_message(topic, message)
    }
}

fun on_message(topic: String, message: MqttMessage) {
    println("📩 Received: '${String(message.payload)}' on topic '$topic'")
}

fun on_subscribe(mid: Int) {
    println("🔔 Subscribed (mid=$mid)")
}

fun on_publish(mid: Int) {
    println("📤 Message $mid sent to broker")
}

// --- MQTT client setup ---
fun setup_mqtt() {
    val clientId = MqttClient.generateClientId()
    client = MqttClient(BROKER_ADDRESS, clientId)

    val options = MqttConnectOptions().apply {
        isCleanSession = true
    }

    client.setCallback(object : MqttCallbackExtended {
        override fun connectionLost(cause: Throwable?) {
            println("⚠️ Connection lost: ${cause?.message}")
        }

        override fun connectComplete(reconnect: Boolean, serverURI: String?) {
            on_connect(reconnect, serverURI)
        }

        override fun messageArrived(topic: String?, message: MqttMessage?) {
            if (topic != null && message != null) {
                on_message(topic, message)
            }
        }

        override fun deliveryComplete(token: IMqttDeliveryToken?) {
            token?.messageId?.let { on_publish(it) }
        }
    })

    client.connect(options)
    // Since Java client doesn't have loop_start, events happen automatically via callback
}

// --- Main control loop ---
fun main() {
    setup_mqtt()

    println("🚀 Điều khiển robot bằng phím WASD, nhấn 'q' để thoát")

    while (true) {
        val key = get_key().lowercase()
        var cmd = ""
        when (key) {
            "w" -> cmd = "Forward"
            "s" -> cmd = "Backward"
            "a" -> cmd = "Left"
            "d" -> cmd = "Right"
            " " -> cmd = "Stop"
            "q" -> {
                println("❌ Thoát chương trình.")
                break
            }
        }

        if (cmd.isNotEmpty()) {
            val message = MqttMessage(cmd.toByteArray())
            client.publish(TOPIC, message)
            println("➡️  Gửi: $cmd")
        }
    }

    client.disconnect()
    client.close()
}