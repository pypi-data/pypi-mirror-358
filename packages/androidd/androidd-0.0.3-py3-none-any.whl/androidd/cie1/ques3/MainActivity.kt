package com.example.labexam_03

import android.os.Bundle
import android.support.v7.app.AppCompatActivity
import android.widget.Button
import android.widget.TextView
import android.widget.Toast

class MainActivity : AppCompatActivity() {
    private var count = 0

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val tvCounter = findViewById<TextView>(R.id.tvCounter)
        val btnIncrement = findViewById<Button>(R.id.btnIncrement)
        val btnToast = findViewById<Button>(R.id.btnToast)

        btnIncrement.setOnClickListener {
            count++
            tvCounter.text = count.toString()
        }

        btnToast.setOnClickListener {
            Toast.makeText(this, "Hello from Toast!", Toast.LENGTH_SHORT).show()
        }
    }
}
