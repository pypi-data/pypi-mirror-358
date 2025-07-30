package com.example.practice

import android.app.TimePickerDialog
import android.os.Bundle
import android.support.v7.app.AppCompatActivity
import android.widget.Button
import android.widget.TextView
import java.util.*

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val btnPickTime = findViewById<Button>(R.id.btnPickTime)
        val tvSelectedTime = findViewById<TextView>(R.id.tvSelectedTime)

        btnPickTime.setOnClickListener {
            val calendar = Calendar.getInstance()
            val hour = calendar.get(Calendar.HOUR_OF_DAY)
            val minute = calendar.get(Calendar.MINUTE)

            val timePicker = TimePickerDialog(this, { _, h, m ->
                tvSelectedTime.text = "Selected Time: $h:$m"
            }, hour, minute, true)

            timePicker.show()
        }
    }
}
