package com.example.practice


import android.os.Bundle
import android.support.v7.app.AppCompatActivity
import android.widget.RadioButton
import android.widget.RadioGroup
import android.widget.Toast

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val radioGroup = findViewById<RadioGroup>(R.id.radioGroup)

        radioGroup.setOnCheckedChangeListener { _, checkedId ->
            val radio = findViewById<RadioButton>(checkedId)
            Toast.makeText(this, "Selected: ${radio.text}", Toast.LENGTH_SHORT).show()
        }
    }
}
