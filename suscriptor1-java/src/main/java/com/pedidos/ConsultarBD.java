package com.pedidos;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;

/** Utilidad: imprime la tabla "pedidos" para comprobar lo que guardó el Suscriptor 1. */
public class ConsultarBD {
    public static void main(String[] args) throws Exception {
        try (Connection bd = DriverManager.getConnection("jdbc:sqlite:pedidos.db");
             Statement st = bd.createStatement();
             ResultSet rs = st.executeQuery("SELECT id, producto, cantidad FROM pedidos ORDER BY id")) {
            System.out.printf("%-5s | %-15s | %s%n", "id", "producto", "cantidad");
            System.out.println("------+-----------------+---------");
            while (rs.next()) {
                System.out.printf("%-5d | %-15s | %d%n",
                        rs.getInt("id"), rs.getString("producto"), rs.getInt("cantidad"));
            }
        }
    }
}
