package com.pedidos;

import com.rabbitmq.client.Channel;
import com.rabbitmq.client.Connection;
import com.rabbitmq.client.ConnectionFactory;
import com.rabbitmq.client.DeliverCallback;
import org.json.JSONObject;

import java.nio.charset.StandardCharsets;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.Statement;

/**
 * Suscriptor 1 (Java)
 */
public class Suscriptor1 {

    private static final String RABBIT_URL = "amqp://guest:guest@localhost:5672";
    private static final String EXCHANGE = "ropa_exchange";
    private static final String MARCA = "adidas";
    private static final String COLA = "cola_adidas";
    private static final String URL_BD = "jdbc:sqlite:pedidos.db";

    public static void main(String[] args) throws Exception {
        java.sql.Connection bd = DriverManager.getConnection(URL_BD);
        try (Statement st = bd.createStatement()) {
            st.execute("""
                CREATE TABLE IF NOT EXISTS pedidos (
                    id       INTEGER PRIMARY KEY AUTOINCREMENT,
                    producto TEXT    NOT NULL,
                    cantidad INTEGER NOT NULL
                )""");
        }
        PreparedStatement insertar =
                bd.prepareStatement("INSERT INTO pedidos (producto, cantidad) VALUES (?, ?)");

        ConnectionFactory factory = new ConnectionFactory();
        factory.setUri(RABBIT_URL);
        Connection conexion = factory.newConnection();
        Channel canal = conexion.createChannel();

        canal.exchangeDeclare(EXCHANGE, "direct", true);
        canal.queueDeclare(COLA, true, false, false, null);
        canal.queueBind(COLA, EXCHANGE, MARCA);

        System.out.println("[Suscriptor 1 - Java] Suscrito a '" + MARCA + "' (cola '" + COLA + "'). CTRL+C para salir.");

        DeliverCallback alRecibir = (etiqueta, entrega) -> {
            String cuerpo = new String(entrega.getBody(), StandardCharsets.UTF_8);
            long tag = entrega.getEnvelope().getDeliveryTag();
            try {
                JSONObject json = new JSONObject(cuerpo);
                String producto = json.getString("producto");
                int cantidad = json.getInt("cantidad");

                insertar.setString(1, producto);
                insertar.setInt(2, cantidad);
                insertar.executeUpdate();

                System.out.println("  Guardado en BD -> producto=" + producto + ", cantidad=" + cantidad);
                canal.basicAck(tag, false);
            } catch (Exception e) {
                System.err.println("  Mensaje inválido descartado: " + cuerpo + " (" + e.getMessage() + ")");
                canal.basicNack(tag, false, false);
            }
        };

        canal.basicConsume(COLA, false, alRecibir, etiqueta -> { });
    }
}
