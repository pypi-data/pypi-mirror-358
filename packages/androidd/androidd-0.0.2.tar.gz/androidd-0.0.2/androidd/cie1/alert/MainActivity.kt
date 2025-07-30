package com.example.practice

import android.os.Bundle
import android.support.v7.app.AppCompatActivity
import android.support.v7.app.AlertDialog
import android.widget.Button
import android.widget.Toast

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val btnShowDialog = findViewById<Button>(R.id.btnShowDialog)

        btnShowDialog.setOnClickListener {
            AlertDialog.Builder(this)
                .setTitle("Exit Confirmation")
                .setMessage("Do you really want to exit?")
                .setPositiveButton("Yes") { _, _ ->
                    Toast.makeText(this, "Exiting...", Toast.LENGTH_SHORT).show()
                    finish()
                }
                .setNegativeButton("No", null)
                .show()
        }
    }
}
