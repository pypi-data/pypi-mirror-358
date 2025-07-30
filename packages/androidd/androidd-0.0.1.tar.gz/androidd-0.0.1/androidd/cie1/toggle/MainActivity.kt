package com.example.practice

import android.os.Bundle
import android.support.v7.app.AppCompatActivity
import android.widget.TextView
import android.widget.ToggleButton

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val toggleButton = findViewById<ToggleButton>(R.id.toggleButton)
        val tvStatus = findViewById<TextView>(R.id.tvStatus)

        toggleButton.setOnCheckedChangeListener { _, isChecked ->
            tvStatus.text = if (isChecked) "Status: ON" else "Status: OFF"
        }
    }
}
