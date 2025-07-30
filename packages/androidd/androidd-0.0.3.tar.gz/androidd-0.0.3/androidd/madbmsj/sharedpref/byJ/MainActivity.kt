package com.example.practice

import android.os.Bundle
import android.support.v7.app.AppCompatActivity
import android.widget.*

class MainActivity : AppCompatActivity() {
    private val PREFS_NAME = "MyPrefs"
    private val KEY_NAME = "username"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val etName = findViewById<EditText>(R.id.etName)
        val btnSave = findViewById<Button>(R.id.btnSave)
        val tvDisplay = findViewById<TextView>(R.id.tvDisplay)

        val prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE)
        val savedName = prefs.getString(KEY_NAME, "No name saved")
        tvDisplay.text = "Saved Name: $savedName"

        btnSave.setOnClickListener {
            val name = etName.text.toString()
            if (name.isNotEmpty()) {
                prefs.edit().putString(KEY_NAME, name).apply()
                tvDisplay.text = "Saved Name: $name"
                Toast.makeText(this, "Name saved", Toast.LENGTH_SHORT).show()
            } else {
                Toast.makeText(this, "Please enter a name", Toast.LENGTH_SHORT).show()
            }
        }
    }
}
